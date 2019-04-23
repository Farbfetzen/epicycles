"""Draw various intricate shapes by adding rotating circles.


Copyright (C) 2019 Sebastian Henz

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


import os
import math
from numpy.fft import ifft
import argparse

# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame as pg


# TODO: Load harmonics from file if given a filename. Modify the file format
# output by the R script, i.e. remove the brackets and trailing commas.

# aalines don't look right. They always have some gaps in between them.
# So instead of using aalines I draw non-aalines but onto a big surface
# which gets smoothscaled down into the window. This produces a nice looking
# result, is fast and easy.

# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i" in math and physics
# c is the position of the circle center

DEFAULT_WINDOW_WIDTH = 700
DEFAULT_WINDOW_HEIGHT = 700
SMOOTH_SCALE_FACTOR = 1.5  # < 2 for performance but > 1 nice looking result
FPS = 30
BACKGROUND_COLOR = (255, 255, 255)
PATH_COLOR = (255, 0, 0)
CIRCLE_COLOR = (170, 170, 170)
CIRCLE_LINE_COLOR = (60, 60, 60)
MIN_SPEED = 1/16
MAX_SPEED = 16
DEFAULT_SCALE_FACTOR = 0.8
CIRCLE_LINE_THICKNESS = 1
PATH_LINE_THICKNESS = 3


class Epicycles:
    """
    points_file: File containing the points of the image as x and y coordinates
        separated by whitespace and on seprate lines.
    n: Maximum number of harmonics.
    scale_factor: A number > 0 and <= 1 indicating how much of the width and
        height of the window the shape should occupy. To disable rescaling
        leave it at the default (None).
    """
    def __init__(self, points_file, n, scale_factor, fade, invert_rotation):
        self.running = True
        self.speed = 1  # speed of the innermost circle in radians/second
        self.paused = False
        self.circles_visible = True
        self.fade = fade
        self.angle = 0  # angle in radians
        self.angle_increment = 0
        # Create clock instance in self.run() so time doesn't run during setup.
        self.clock = None

        # Setup surfaces:
        # TODO: Make the default window size adjustable via command line arguments
        self.window_width = DEFAULT_WINDOW_WIDTH
        self.window_height = DEFAULT_WINDOW_HEIGHT
        display_info = pg.display.Info()
        display_width = display_info.current_w
        display_height = display_info.current_h
        if DEFAULT_WINDOW_WIDTH >= display_width:
            self.window_width = display_width - 200
            self.window_height = self.window_width
        if DEFAULT_WINDOW_HEIGHT >= display_height:
            self.window_height = display_height - 200
            self.window_width = self.window_height

        self.window = pg.display.set_mode(
            (self.window_width, self.window_height)
        )
        pg.display.set_caption("Epicycles")
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
        self.transp_surface.fill(
            (self.alpha_increment, self.alpha_increment, self.alpha_increment)
        )
        self.angle_per_alpha = math.tau / 255 * self.alpha_increment

        # Setup harmonics:
        self.harmonics, offset = self.transform(
            self.load_path(
                points_file, scale_factor
            ),
            invert_rotation
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
            self.window_width // 2 * SMOOTH_SCALE_FACTOR - int(offset[0]),
            self.window_height // 2 * SMOOTH_SCALE_FACTOR - int(offset[1])
        ))
        self.circle_radii = []
        for h in self.harmonics:
            radius = int(abs(h[0]))
            if radius >= CIRCLE_LINE_THICKNESS:
                self.circle_radii.append(radius)
        self.point = []
        self.update_circles(0)
        self.previous_point = self.point

    @staticmethod
    def to_complex(xy):
        return complex(xy[0], xy[1])

    @staticmethod
    def from_complex(z):
        return [z.real, z.imag]

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

        return [complex(*i) for i in zip(all_x, all_y)]

    def transform(self, path, invert=False):
        transformed = ifft(path)
        transformed = list(transformed)
        offset = self.from_complex(transformed.pop(0))
        h = []
        i = 1
        increase_i = False
        sign = 1 if invert else -1
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

    def handle_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                elif event.key == pg.K_p or event.key == pg.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pg.K_c:
                    self.circles_visible = not self.circles_visible
                elif event.key == pg.K_UP:
                    self.speed = min(self.speed * 2, MAX_SPEED)
                elif event.key == pg.K_DOWN:
                    self.speed = max(self.speed / 2, MIN_SPEED)
                elif event.key == pg.K_BACKSPACE:
                    self.line_surface.fill(BACKGROUND_COLOR)
                elif DEBUG_MODE and event.key == pg.K_d:
                    info = f"\nangle: {round(self.angle, 3)} radians" + \
                           f" ({round(math.degrees(self.angle), 2)}°)" + \
                           f"\nspeed: {self.speed}" + \
                           f"\nfps: {int(self.clock.get_fps())}"
                    print(info)

    def update_circles(self, dt):
        self.angle_increment = self.speed * dt
        self.angle += self.angle_increment
        if self.angle > math.tau:
            self.angle -= math.tau
        for i, h in enumerate(self.harmonics):
            p = h[0] * math.e ** (h[1] * self.angle) + self.circle_points[i]
            self.circle_points[i+1] = p
        self.previous_point = self.point
        self.point = self.from_complex(self.circle_points[-1])

    def draw(self):
        if not self.paused:
            if self.fade:
                self.alpha_angle += self.angle_increment
                while self.alpha_angle > self.angle_per_alpha:
                    self.line_surface.blit(
                        self.transp_surface,
                        (0, 0),
                        special_flags=pg.BLEND_RGBA_ADD
                    )
                    self.alpha_angle -= self.angle_per_alpha
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
            self.window
        )

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:
            dt = self.clock.tick(FPS) / 1000  # seconds
            self.handle_input()
            if not self.paused:
                self.update_circles(dt)
            self.draw()
            pg.display.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="Path to file containing the points of the shape."
    )
    parser.add_argument(
        "-n",
        type=int,
        help="Maximum number of harmonics or circles.",
        metavar="",
        default = None
    )
    parser.add_argument(
        "-s",
        "--scale_factor",
        type=float,
        metavar="",
        help="A number > 0 and <= 1 indicating how much of the width and " +
             "height of the window the shape should occupy. To disable " +
             f"rescaling set it to 0. Defaults to {DEFAULT_SCALE_FACTOR}.",
        default=DEFAULT_SCALE_FACTOR
    )
    parser.add_argument(
        "-f",
        "--fade",
        action="store_true",
        help="Fade the line over time so that it vanishes after one cycle."
    )
    parser.add_argument(
        "-i",
        "--invert",
        action="store_true",
        help="Invert the rotation direction of all circles."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Debug mode."
    )
    args = parser.parse_args()
    DEBUG_MODE = args.debug

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pg.init()
    E = Epicycles(
        args.file,
        args.n,
        args.scale_factor,
        args.fade,
        args.invert
    )
    E.run()
