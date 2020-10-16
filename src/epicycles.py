import math
import numpy.fft

import pygame
import pygame.gfxdraw

from src import constants


class Epicycles:
    def __init__(self, filename, n,
                 scale, fade, reverse, target_surface_rect):
        self.speed_index = 3
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
        self.angle = 0  # in radians
        self.angles = [self.angle, self.angle]
        p = self.get_point_at_angle(self.angle)
        self.points = [p, p]

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
        self.angle = self.angle + self.angular_velocity * dt
        previous_point = self.points[-1]
        next_point = self.get_point_at_angle(self.angle)
        dist = previous_point.distance_to(next_point)
        if dist < 1:
            return
        elif dist > constants.MAX_DIST:
            interpolated_points, interpolated_angles = self.interpolate(
                        previous_point,
                        next_point,
                        self.angles[-1],
                        self.angle
                    )
            for angle in reversed(interpolated_angles):
                if 0 <= angle < math.tau:
                    break
                angle %= math.tau
            new_points = interpolated_points.append(next_point)
            new_angles = interpolated_angles.append(self.angle)
        else:
            new_points = next_point
            new_angles = self.angle

        self.trim()

        self.angles += new_angles
        self.points += new_points

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

    def get_point_at_angle(self, angle):
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
        """Add more points in between if two points are too far apart."""
        mean_angle = (a1 + a2) / 2
        mean_point = self.get_point_at_angle(mean_angle)
        result_points = []
        result_angles = []
        if p1.distance_to(mean_point) > constants.MAX_DIST:
            interp_points, interp_angles = self.interpolate(p1, mean_point,
                                                            a1, mean_angle)
            result_points += interp_points
            result_angles += interp_angles
        result_points.append(mean_point)
        result_angles.append(mean_angle)
        if mean_point.distance_to(p2) > constants.MAX_DIST:
            interp_points, interp_angles = self.interpolate(mean_point, p2,
                                                            mean_angle, a2)
            result_points += interp_points
            result_angles += interp_angles
        return result_points, result_angles

    def trim(self):
        """Keep the points and angles lists short by
        removing old points that are more than tau radians behind.
        Also correct the angle so that it is always between 0 and tau.
        """
        oldest_angle = self.angles[0]
        if self.velocity_positive:
            if self.angle >= math.tau:
                for i, angle in enumerate(self.angles):
                    if angle < oldest_angle:
                        self.angles = self.angles[i:]
                        self.points = self.points[i:]
                        break
            self.angle %= math.tau
            if self.angles[0] < self.angle:
                for i, angle in enumerate(self.angles):
                    if angle > self.angle:
                        self.angles = self.angles[i:]
                        self.points = self.points[i:]
                        break
        else:
            if self.angle < 0:
                for i, angle in enumerate(self.angles):
                    if angle > oldest_angle:
                        self.angles = self.angles[i:]
                        self.points = self.points[i:]
                        break
            self.angle %= math.tau
            if self.angles[0] > self.angle:
                for i, angle in enumerate(self.angles):
                    if angle < self.angle:
                        self.angles = self.angles[i:]
                        self.points = self.points[i:]
                        break

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
        # TODO: is this true? Test it!
        self.erase_line()

    def erase_line(self):
        # Keep the last two points so the draw functions don't complain.
        self.points = self.points[-2:]
        self.angles = self.angles[-2:]

    @staticmethod
    def complex_to_vec2(z):
        return pygame.Vector2(z.real, z.imag)
