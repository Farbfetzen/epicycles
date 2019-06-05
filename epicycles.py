"""Copyright (C) 2019 Sebastian Henz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import math
from numpy.fft import ifft

import pygame as pg


# TODO: Load harmonics from file if given a filename. Modify the file format
#       output by the R script, i.e. remove the brackets and trailing commas.

# aalines don't look right. They always have some gaps in between them.
# So instead of using aalines I draw non-aalines but onto a big surface
# which gets smoothscaled down into the window. This produces a nice looking
# result in a fast and easy way.

# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i" in math and physics
# c is the position of the circle center

PATH_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
CIRCLE_COLOR = (170, 170, 170)
CIRCLE_LINE_COLOR = (60, 60, 60)
CIRCLE_LINE_THICKNESS = 1
PATH_LINE_THICKNESS = 3
SMOOTH_SCALE_FACTOR = 1.5  # < 2 for performance but > 1 nice looking result
# Max. distance between two points before interpolation kicks in:
MAX_DIST = 5 * SMOOTH_SCALE_FACTOR
MIN_SPEED = 1/16
MAX_SPEED = 4


class Epicycles:
    def __init__(self, window_width, window_height, points_file, n,
                 scale_factor, fade, reverse_rotation):
        self.speed = 1  # speed of the innermost circle in radians/second
        self.circles_visible = True
        self.fade = fade
        self.angle = 0  # angle in radians
        self.previous_angle = self.angle
        self.angle_increment = 0

        self.window_width = window_width
        self.window_height = window_height

        self.big_surface = pg.Surface((
            self.window_width * SMOOTH_SCALE_FACTOR,
            self.window_height * SMOOTH_SCALE_FACTOR
        ))
        self.line_surface = self.big_surface.copy()
        self.transp_surface = self.line_surface.copy()
        self.line_surface.fill(BACKGROUND_COLOR)
        self.alpha_angle = 0
        # self.alpha_increment is best left at 5. Smaller numbers cause more
        # blits per frame of the transparent surface which may cause framerate
        # issues. Larger numbers make the line fade in a choppy looking way.
        self.alpha_increment = 5
        self.angle_per_alpha = math.tau / 255 * self.alpha_increment
        self.transp_surface.fill(
            (self.alpha_increment, self.alpha_increment, self.alpha_increment)
        )

        # Setup harmonics:
        self.harmonics, offset = self.transform(
            self.load_path(
                points_file, scale_factor
            ),
            reverse_rotation
        )
        if n is not None:
            if n > 0:
                self.harmonics = self.harmonics[:n]
            else:
                raise ValueError("n must be positive.")
        # Invert y-axis for pygame window:
        for i, h in enumerate(self.harmonics):
            z = h[0]
            self.harmonics[i][0] = complex(z.real, z.imag * -1)

        # Setup circles and points:
        self.circle_points = [0j] * (len(self.harmonics) + 1)
        self.circle_points[0] = self.to_complex((
            window_width // 2 * SMOOTH_SCALE_FACTOR - int(offset[0]),
            window_height // 2 * SMOOTH_SCALE_FACTOR - int(offset[1])
        ))
        self.circle_radii = []
        for h in self.harmonics:
            radius = int(abs(h[0]))
            if radius >= CIRCLE_LINE_THICKNESS:
                self.circle_radii.append(radius)
        self.previous_point = ()
        self.point = self.get_new_point(self.angle)
        self.interpolated_points = ()

    def draw(self, target_surf, paused):
        if not paused:
            if self.fade:
                self.alpha_angle += self.angle_increment
                while self.alpha_angle > self.angle_per_alpha:
                    self.line_surface.blit(
                        self.transp_surface,
                        (0, 0),
                        special_flags=pg.BLEND_RGBA_ADD
                    )
                    self.alpha_angle -= self.angle_per_alpha
            if self.interpolated_points:
                pg.draw.lines(
                    self.line_surface,
                    PATH_COLOR,
                    False,
                    self.interpolated_points,
                    PATH_LINE_THICKNESS
                )
            else:
                pg.draw.line(
                    self.line_surface,
                    PATH_COLOR,
                    self.previous_point,
                    self.point,
                    PATH_LINE_THICKNESS
                )
        self.big_surface.blit(self.line_surface, (0, 0))

        if self.circles_visible:
            xy_points = [[int(xy) for xy in self.from_complex(i)]
                         for i in self.circle_points]
            for i, r in enumerate(self.circle_radii):
                pg.draw.circle(
                    self.big_surface,
                    CIRCLE_COLOR,
                    xy_points[i],
                    r,
                    CIRCLE_LINE_THICKNESS
                )
            pg.draw.lines(
                self.big_surface,
                CIRCLE_LINE_COLOR,
                False,
                xy_points,
                CIRCLE_LINE_THICKNESS
            )
        pg.transform.smoothscale(
            self.big_surface,
            (self.window_width, self.window_height),
            target_surf
        )

    def erase_line(self):
        self.line_surface.fill(BACKGROUND_COLOR)

    @staticmethod
    def from_complex(z):
        return z.real, z.imag

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
        if self.get_dist(p1, new_point) > MAX_DIST:
            result += self.interpolate(p1, new_point, a1, mean_angle)
        result += (new_point, )
        if self.get_dist(new_point, p2) > MAX_DIST:
            result += self.interpolate(new_point, p2, mean_angle, a2)
        return result

    def load_path(self, points_file, scale_factor):
        all_x = []
        all_y = []
        with open(points_file, "r") as file:
            for line in file:
                x, y = line.split()
                all_x.append(float(x))
                all_y.append(float(y))

        if scale_factor != 0:
            if 0 < scale_factor <= 1:
                max_allowed_x = self.window_width / 2 * scale_factor
                max_allowed_y = self.window_height / 2 * scale_factor
                if max_allowed_x <= max_allowed_y:
                    ratio = max_allowed_x / max(map(abs, all_x))
                    all_x = [x * ratio for x in all_x]
                    all_y = [y * ratio for y in all_y]
                else:
                    ratio = max_allowed_y / max(map(abs, all_y))
                    all_x = [x * ratio for x in all_x]
                    all_y = [y * ratio for y in all_y]
            else:
                raise ValueError(
                    "Argument 'scale_factor' must be between 0 and 1."
                )
            all_x = [x * SMOOTH_SCALE_FACTOR for x in all_x]
            all_y = [y * SMOOTH_SCALE_FACTOR for y in all_y]

        return [complex(*xy) for xy in zip(all_x, all_y)]

    def speed_down(self):
        self.speed = max(self.speed / 2, MIN_SPEED)

    def speed_up(self):
        self.speed = min(self.speed * 2, MAX_SPEED)

    @staticmethod
    def to_complex(xy):
        return complex(xy[0], xy[1])

    def transform(self, path, reverse=False):
        transformed = ifft(path)
        transformed = list(transformed)
        offset = self.from_complex(transformed.pop(0))
        h = []
        i = 1
        increase_i = False
        sign = 1 if reverse else -1
        pop_back = True  # pop from the front or the back
        while transformed:
            radius = transformed.pop(-pop_back)
            if abs(radius) >= 0.1:
                h.append([radius, complex(0, sign * i)])
            if increase_i:
                i += 1
            increase_i = not increase_i
            sign *= -1
            pop_back = not pop_back
        return h, offset

    def update(self, dt):
        self.previous_angle = self.angle
        self.angle_increment = self.speed * dt
        self.angle += self.angle_increment
        self.previous_point = self.point
        self.point = self.get_new_point(self.angle)

        if self.get_dist(self.previous_point, self.point) > MAX_DIST:
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
