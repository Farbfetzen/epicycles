import math
import numpy.fft

import pygame
import pygame.gfxdraw

from src import constants


class Epicycles:
    def __init__(self, filename, n,
                 scale, fade, reverse, target_surface_rect):
        self.speed_index = 3
        # speed of the innermost circle in radians/second-
        self.angular_velocity = constants.SPEEDS[self.speed_index]
        if reverse:
            self.angular_velocity *= -1
        self.velocity_positive = self.angular_velocity > 0
        self.circles_visible = True
        self.fade = fade

        self.harmonics, offset = self.load_file(
            filename,
            scale,
            target_surface_rect
        )
        if n > 0:
            self.harmonics = self.harmonics[:n]

        self.circle_centers = [0j] * (len(self.harmonics) + 1)
        self.circle_centers[0] = complex(
            target_surface_rect.centerx - int(offset.x),
            target_surface_rect.centery - int(offset.y)
        )
        self.circle_radii = []
        for h in self.harmonics:
            radius = int(abs(h[0]))
            # Only add circle if radius is large enough for it to be visible.
            # Make it int because gfxdraw needs integer arguments.
            if radius >= 1:
                self.circle_radii.append(radius)

        # Add the points twice so the line draw functions don't complain when
        # the app is started in the paused state.
        p = self.get_next_point(0)
        self.points = [p, p]
        self.angles = [0, 0]  # angles in radians

    def load_file(self, filename, scale, target_surface_rect):
        with open(filename, "r") as file:
            file_type = file.readline().strip()
            if file_type == "shape":
                points = []
                for line in file:
                    x, y = line.split()
                    # Flip the image by negating y because in pygame y=0
                    # is at the top.
                    points.append(pygame.Vector2(float(x), -float(y)))
                harmonics, offset = self.transform_coordinates(
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

    def transform_coordinates(self, points, scale_factor, target_surface_rect):
        # TODO: Break this up into three methods.

        # Center the shape around (0, 0):
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
        offset = pygame.Vector2(self.complex_to_vec2(transformed.pop(0))) * -1
        harmonics = []
        i = 1
        increase_i = False
        sign = -1
        pop_back = False  # pop from the front or the back
        while transformed:
            radius = transformed.pop(-pop_back)
            # Only add harmonics over a certain radius threshold to ignore
            # harmonics which don't noticeably contribute.
            if abs(radius) >= 0.1:
                harmonics.append([radius, complex(0, sign * i)])
            if increase_i:
                i += 1
            increase_i = not increase_i
            sign *= -1
            pop_back = not pop_back

        return harmonics, offset

    def update(self, dt):
        next_angle = self.angles[-1] + self.angular_velocity * dt
        next_point = self.get_next_point(next_angle)

        # TODO: re-enable interpolation later
        # if self.previous_point.distance_to(self.point) > constants.MAX_DIST:
        #     self.interpolated_points = (
        #             (self.previous_point,) +
        #             self.interpolate(
        #                 self.previous_point,
        #                 self.point,
        #                 self.previous_angle,
        #                 self.angle
        #             ) +
        #             (self.point,)
        #     )
        # else:
        #     self.interpolated_points = ()

        self.trim_lists(next_angle)

        # Must be done after the interpolation and list trimming
        # or else those won't work.
        next_angle %= math.tau

        # TODO: append the interpolated list instead
        self.angles.append(next_angle)
        self.points.append(next_point)

    def draw(self, target_surf):
        pygame.draw.aalines(
            target_surf,
            constants.PATH_COLOR,
            False,
            self.points
        )

        if self.circles_visible:
            # Integer centers because gfxdraw needs integer coordinates.
            centers = [[int(p) for p in self.complex_to_vec2(cc)]
                       for cc in self.circle_centers]
            for center, radius in zip(centers, self.circle_radii):
                pygame.gfxdraw.aacircle(
                    target_surf,
                    center[0],
                    center[1],
                    int(radius),
                    constants.CIRCLE_COLOR
                )
            pygame.draw.aalines(
                target_surf,
                constants.CIRCLE_COLOR,
                False,
                centers
            )

    def get_next_point(self, angle):
        # This is the formula:
        # a * exp(bj * t) + c
        # a is the amplitude (circle radius)
        # b is the angular speed (negative values rotate anticlockwise)
        # j is sqrt(-1), usually denoted "i" in math and physics
        # t is the current angle
        # c is the position of the circle center

        for i, h in enumerate(self.harmonics):
            self.circle_centers[i + 1] = \
                h[0] * math.e ** (h[1] * angle) + self.circle_centers[i]
        return self.complex_to_vec2(self.circle_centers[-1])

    def interpolate(self, p1, p2, a1, a2):
        # FIXME: Why tuple? Append to list!
        mean_angle = (a1 + a2) / 2
        new_point = self.get_next_point(mean_angle)
        result = ()
        if p1.distance_to(new_point) > constants.MAX_DIST:
            result += self.interpolate(p1, new_point, a1, mean_angle)
        result += (new_point, )
        if new_point.distance_to(p2) > constants.MAX_DIST:
            result += self.interpolate(new_point, p2, mean_angle, a2)
        return result

    def trim_lists(self, next_angle):
        """Keep the points and angles lists short by
        removing redundant points.
        """
        # FIXME: Does not work around angle=0 because there it flips between 0 and 2pi.
        # FIXME: Does not seem to work for negative rotation direction.

        # Maybe have a special condition for when next_angle is > 2pi.

        for i, angle in enumerate(self.angles):
            if ((self.velocity_positive and angle > next_angle)
                    or (not self.velocity_positive and angle < next_angle)):
                break
        else:
            return
        if i > 0:
            #print(f"{i=}, {angle=:.4f}, {next_angle=:.4f}")
            self.points = self.points[i:]
            self.angles = self.angles[i:]

    def increase_speed(self):
        self.speed_index = min(self.speed_index + 1, len(constants.SPEEDS) - 1)
        self.angular_velocity = math.copysign(
            constants.SPEEDS[self.speed_index],
            self.angular_velocity
        )

    def decrease_speed(self):
        self.speed_index = max(self.speed_index - 1, 0)
        self.angular_velocity = math.copysign(
            constants.SPEEDS[self.speed_index],
            self.angular_velocity
        )

    def reverse_direction(self):
        self.angular_velocity *= -1
        self.velocity_positive = not self.velocity_positive
        # Trim the point and angle lists here, otherwise there is a
        # possibility for them to become too long which may slow down the app.
        self.erase_line()

    def erase_line(self):
        # Keep the last two points so the draw functions don't complain.
        self.points = self.points[-2:]
        self.angles = self.angles[-2:]

    @staticmethod
    def complex_to_vec2(z):
        return pygame.Vector2(z.real, z.imag)
