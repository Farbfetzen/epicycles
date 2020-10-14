import math
import numpy.fft

import pygame

from src import constants


# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i" in math and physics
# c is the position of the circle center


class Epicycles:
    def __init__(self, filename, n,
                 scale, fade, reverse, target_surface_rect):
        window_width, window_height = target_surface_rect.size
        self.speed = 1  # speed of the innermost circle in radians/second
        self.circles_visible = True
        self.fade = fade
        self.angle = 0  # angle in radians
        self.previous_angle = self.angle
        self.angle_increment = 0

        self.window_width = window_width
        self.window_height = window_height

        # Setup harmonics:
        self.harmonics, offset = self.load_file(
            filename,
            scale,
            target_surface_rect
        )
        if n > 0:
            self.harmonics = self.harmonics[:n]

        # Setup circles and points:
        self.circle_points = [0j] * (len(self.harmonics) + 1)
        self.circle_points[0] = self.to_complex((
            window_width // 2 - int(offset[0]),
            window_height // 2 - int(offset[1])
        ))
        self.circle_radii = []
        for h in self.harmonics:
            radius = int(abs(h[0]))
            # Only add circle if radius is large enough for it to be visible:
            if radius >= 1:
                self.circle_radii.append(radius)
        self.previous_point = ()
        self.point = self.get_new_point(self.angle)
        self.interpolated_points = ()

    def load_file(self, filename, scale, target_surface_rect):
        with open(filename, "r") as file:
            file_type = file.readline().strip()
            if file_type == "shape":
                points = []
                for line in file:
                    x, y = line.split()
                    # Use negative y because in pygame the origin is topleft.
                    p = pygame.Vector2(float(x), -float(y))
                    points.append(p)
                harmonics, offset = self.get_harmonics(
                    points,
                    scale,
                    target_surface_rect
                )
            elif file_type == "harmonics":
                # TODO: Implement this. Remember to scale these.
                raise NotImplementedError("Harmonic files can not yet be read.")
            else:
                raise ValueError(
                    "Unknown file type. First line in file must be either " +
                    "\"shape\" or \"harmonics\""
                )
        return harmonics, offset

    def get_harmonics(self, points, scale_factor, target_surface_rect):
        # Center the shape around (0,0):
        max_x = max(points, key=lambda vec: vec.x).x
        min_x = min(points, key=lambda vec: vec.x).x
        max_y = max(points, key=lambda vec: vec.y).y
        min_y = min(points, key=lambda vec: vec.y).y
        center = pygame.Vector2(
            (max_x + min_x) / 2,
            (max_y + min_y) / 2
        )
        for p in points:
            p -= center

        # Scale the shape relative to scale factor and window size:
        if scale_factor < 0 or scale_factor > 1:
            raise ValueError("Argument \"--scale\" must be between 0 and 1.")
        if scale_factor != 0:
            max_allowed_x = scale_factor * target_surface_rect.centerx
            max_allowed_y = scale_factor * target_surface_rect.centery
            if max_allowed_x <= max_allowed_y:
                ratio = max_allowed_x / (max_x - center.x)
            else:
                ratio = max_allowed_y / (max_y - center.y)
            for p in points:
                p *= ratio

        # Transform:
        complex_points = [complex(*p) for p in points]
        transformed = list(numpy.fft.ifft(complex_points))
        offset = pygame.Vector2(self.from_complex(transformed.pop(0)))
        offset.y *= -1
        harmonics = []
        i = 1
        increase_i = False
        sign = 1
        pop_back = True  # pop from the front or the back
        while transformed:
            radius = transformed.pop(-pop_back)
            # Only add circles over a certain size threshold to prevent
            # spamming tiny circles or circles with radius 0:
            if abs(radius) >= 0.1:
                harmonics.append([radius, complex(0, sign * i)])
            if increase_i:
                i += 1
            increase_i = not increase_i
            sign *= -1
            pop_back = not pop_back

        return harmonics, offset

    def draw(self, target_surf):
        if self.interpolated_points:
            pygame.draw.lines(
                target_surf,
                constants.PATH_COLOR,
                False,
                self.interpolated_points
            )
        else:
            pygame.draw.line(
                target_surf,
                constants.PATH_COLOR,
                self.previous_point,
                self.point
            )

        if self.circles_visible:
            xy_points = [[int(xy) for xy in self.from_complex(i)]
                         for i in self.circle_points]
            for i, r in enumerate(self.circle_radii):
                pygame.draw.circle(
                    target_surf,
                    constants.CIRCLE_COLOR,
                    xy_points[i],
                    r,
                    1
                )
            pygame.draw.lines(
                target_surf,
                constants.CIRCLE_LINE_COLOR,
                False,
                xy_points
            )
        pygame.transform.smoothscale(
            target_surf,
            (self.window_width, self.window_height),
            target_surf
        )

    @staticmethod
    def from_complex(z):
        return pygame.Vector2(z.real, z.imag)

    @staticmethod
    def get_dist(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def get_new_point(self, angle):
        for i, h in enumerate(self.harmonics):
            p = h[0] * math.e ** (h[1] * angle) + self.circle_points[i]
            self.circle_points[i + 1] = p
        return self.from_complex(self.circle_points[-1])

    def interpolate(self, p1, p2, a1, a2):
        mean_angle = (a1 + a2) / 2
        new_point = self.get_new_point(mean_angle)
        result = ()
        if self.get_dist(p1, new_point) > constants.MAX_DIST:
            result += self.interpolate(p1, new_point, a1, mean_angle)
        result += (new_point, )
        if self.get_dist(new_point, p2) > constants.MAX_DIST:
            result += self.interpolate(new_point, p2, mean_angle, a2)
        return result

    def speed_down(self):
        self.speed = max(self.speed / 2, constants.MIN_SPEED)

    def speed_up(self):
        self.speed = min(self.speed * 2, constants.MAX_SPEED)

    @staticmethod
    def to_complex(xy):
        return complex(xy[0], xy[1])

    def update(self, dt):
        self.previous_angle = self.angle
        self.angle_increment = self.speed * dt
        self.angle += self.angle_increment
        self.previous_point = self.point
        self.point = self.get_new_point(self.angle)

        if self.get_dist(self.previous_point, self.point) > constants.MAX_DIST:
            self.interpolated_points = (
                    (self.previous_point,) +
                    self.interpolate(
                        self.previous_point,
                        self.point,
                        self.previous_angle,
                        self.angle
                    ) +
                    (self.point,)
            )
        else:
            self.interpolated_points = ()

        if self.angle > math.tau:
            self.angle -= math.tau
