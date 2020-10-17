import math
import cmath

import pygame
import pygame.gfxdraw

from src import constants
from src import transform


class Epicycles:
    def __init__(self, filename, n, scale_factor, fade, reverse,
                 target_surface_rect, debug):
        self.angular_velocity = constants.DEFAULT_ANGULAR_VELOCITY
        if reverse:
            self.angular_velocity *= -1
        self.velocity_positive = self.angular_velocity > 0
        self.circles_visible = True
        self.fade = fade

        self.harmonics, self.circle_radii, offset = transform.from_txt(
            filename,
            scale_factor,
            target_surface_rect,
            n
        )

        self.circle_centers = [0j] * (len(self.harmonics) + 1)
        self.circle_centers[0] = complex(*(offset + target_surface_rect.center))

        # Add the points twice so the line draw functions don't complain when
        # the app is started in the paused state.
        self.angle = 0  # in radians
        self.angles = [self.angle, self.angle]
        p = self.get_point_at_angle(self.angle)
        self.points = [p, p]

        if debug:
            print(f"{len(self.harmonics)=}")
            print(f"{len(self.circle_radii)=}")

    def update(self, dt):
        self.angle = self.angle + self.angular_velocity * dt
        previous_point = self.points[-1]
        next_point = self.get_point_at_angle(self.angle)
        dist = previous_point.distance_to(next_point)
        if dist < constants.MIN_DISTANCE:
            return
        elif dist > constants.MAX_DISTANCE:
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
            self.points.extend(interpolated_points)
            self.angles.extend(interpolated_angles)

        self.trim()

        self.angles.append(self.angle)
        self.points.append(next_point)

    def draw(self, target_surf):
        pygame.draw.aalines(
            target_surf,
            constants.PATH_COLOR,
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
        # t is the current angle
        # c is the position of the circle center

        for i, (a, b) in enumerate(self.harmonics):
            self.circle_centers[i + 1] = \
                a * cmath.exp(b * angle) + self.circle_centers[i]
        return transform.complex_to_vec2(self.circle_centers[-1])

    def interpolate(self, p1, p2, a1, a2):
        """Add more points in between if two points are too far apart."""
        mean_angle = (a1 + a2) / 2
        mean_point = self.get_point_at_angle(mean_angle)
        result_points = []
        result_angles = []
        if p1.distance_to(mean_point) > constants.MAX_DISTANCE:
            interp_points, interp_angles = self.interpolate(p1, mean_point,
                                                            a1, mean_angle)
            result_points.extend(interp_points)
            result_angles.extend(interp_angles)
        result_points.append(mean_point)
        result_angles.append(mean_angle)
        if mean_point.distance_to(p2) > constants.MAX_DISTANCE:
            interp_points, interp_angles = self.interpolate(mean_point, p2,
                                                            mean_angle, a2)
            result_points.extend(interp_points)
            result_angles.extend(interp_angles)
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
        # Erase the line here, otherwise it glitches.
        self.erase_line()

    def erase_line(self):
        # Keep the last two points so the draw functions don't complain.
        self.points = self.points[-2:]
        self.angles = self.angles[-2:]
