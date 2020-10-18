import math
import cmath

import pygame
import pygame.gfxdraw

from src import constants
from src import transform


class Epicycles:
    def __init__(self, points, n, fade, reverse,
                 surface_center, debug):
        self.angular_velocity = constants.DEFAULT_ANGULAR_VELOCITY
        if reverse:
            self.angular_velocity *= -1
        self.velocity_positive = self.angular_velocity > 0
        self.circles_visible = True
        self.fade = fade

        self.harmonics, self.circle_radii, offset = transform.transform(points)
        if n > 0:
            self.harmonics = self.harmonics[:n]
            self.circle_radii = self.circle_radii[:n]

        self.circle_centers = [0j] * (len(self.harmonics) + 1)
        self.circle_centers[0] = complex(*(offset + surface_center))

        # Add the points twice so the line draw functions don't complain when
        # the app is started in the paused state.
        self.current_angle = 0  # in radians
        self.angles = [self.current_angle, self.current_angle]
        p = self.get_point_at_angle(self.current_angle)
        self.points = [p, p]

        self.line_colors = []

        if debug:
            print(f"{len(self.harmonics)=}")
            print(f"{len(self.circle_radii)=}")

    def update(self, dt):
        self.current_angle = self.current_angle + self.angular_velocity * dt
        previous_point = self.points[-1]
        next_point = self.get_point_at_angle(self.current_angle)
        dist_sq = previous_point.distance_squared_to(next_point)
        if dist_sq < constants.MIN_DISTANCE_SQ:
            return
        elif dist_sq > constants.MAX_DISTANCE_SQ:
            interpolated_points, interpolated_angles = self.interpolate(
                previous_point,
                next_point,
                self.angles[-1],
                self.current_angle
            )
            for angle in reversed(interpolated_angles):
                if 0 <= angle < math.tau:
                    break
                angle %= math.tau
            self.points.extend(interpolated_points)
            self.angles.extend(interpolated_angles)

        self.trim_line()

        if self.fade:
            self.fade_line()

        self.angles.append(self.current_angle)
        self.points.append(next_point)

    def draw(self, target_surf):
        if self.fade:
            for i, col in enumerate(self.line_colors):
                pygame.draw.aaline(
                    target_surf,
                    col,
                    self.points[i],
                    self.points[i + 1]
                )
        else:
            pygame.draw.aalines(
                target_surf,
                constants.LINE_COLOR,
                False,
                self.points
            )

        if self.circles_visible:
            centers = [transform.complex_to_vec2(cc) for cc in self.circle_centers]
            for center, radius in zip(centers, self.circle_radii):
                pygame.gfxdraw.aacircle(
                    target_surf,
                    int(center.x),
                    int(center.y),
                    radius,
                    constants.CIRCLE_COLOR
                )
            pygame.draw.aalines(
                target_surf,
                constants.CIRCLE_COLOR,
                False,
                centers
            )

    def get_point_at_angle(self, angle):
        # FIXME: This function gets called a lot and takes a big chunk of the
        #  time in a tick. Any way to make it faster? Maybe using numpy
        #  vectorization?

        # This is the formula:
        # a * exp(b * t) + c
        # a is the amplitude (circle radius)
        # b is the angular velocity (speed and direction)
        # t is the angle
        # c is the position of the circle center

        for i, (a, b) in enumerate(self.harmonics):
            self.circle_centers[i + 1] = a * cmath.exp(b * angle) + self.circle_centers[i]
        return transform.complex_to_vec2(self.circle_centers[-1])

    def interpolate(self, p1, p2, a1, a2):
        """Add more points in between if two points are too far apart."""
        mean_angle = (a1 + a2) / 2
        mean_point = self.get_point_at_angle(mean_angle)
        result_points = []
        result_angles = []
        if p1.distance_squared_to(mean_point) > constants.MAX_DISTANCE_SQ:
            interp_points, interp_angles = self.interpolate(p1, mean_point,
                                                            a1, mean_angle)
            result_points.extend(interp_points)
            result_angles.extend(interp_angles)
        result_points.append(mean_point)
        result_angles.append(mean_angle)
        if mean_point.distance_squared_to(p2) > constants.MAX_DISTANCE_SQ:
            interp_points, interp_angles = self.interpolate(mean_point, p2,
                                                            mean_angle, a2)
            result_points.extend(interp_points)
            result_angles.extend(interp_angles)
        return result_points, result_angles

    def trim_line(self):
        """Keep the points and angles lists short by
        removing old points that are more than tau radians behind.
        """
        if self.velocity_positive:
            limit = self.current_angle - math.tau
            for i, angle in enumerate(self.angles):
                if angle > limit:
                    self.angles = self.angles[i:]
                    self.points = self.points[i:]
                    break
        else:
            limit = self.current_angle + math.tau
            for i, angle in enumerate(self.angles):
                if angle < limit:
                    self.angles = self.angles[i:]
                    self.points = self.points[i:]
                    break

    def rotate_faster(self):
        self.angular_velocity = min(
            abs(self.angular_velocity) * 2,
            constants.MAX_ANGULAR_VELOCITY
        )
        if not self.velocity_positive:
            self.angular_velocity *= -1

    def rotate_slower(self):
        self.angular_velocity = max(
            abs(self.angular_velocity) / 2,
            constants.MIN_ANGULAR_VELOCITY
        )
        if not self.velocity_positive:
            self.angular_velocity *= -1

    def reverse_direction(self):
        self.angular_velocity *= -1
        self.velocity_positive = not self.velocity_positive
        # Erase the line here and reverse the remnant, otherwise it glitches.
        self.erase_line()
        self.points.reverse()
        self.angles.reverse()
        self.line_colors.reverse()

    def erase_line(self):
        # Keep the last two points so the draw functions don't complain.
        self.points = self.points[-2:]
        self.angles = self.angles[-2:]
        # Colors list length must be one less than points and angles.
        self.line_colors = self.line_colors[-1:]

    def fade_line(self):
        self.line_colors = []
        for angle in self.angles:
            self.line_colors.append(
                constants.LINE_COLOR.lerp(
                    constants.BACKGROUND_COLOR,
                    abs(self.current_angle - angle) / math.tau
                )
            )
