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

import argparse
import math
import os

# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame as pg

from epicycles import Epicycles


DEFAULT_WINDOW_WIDTH = 700
DEFAULT_WINDOW_HEIGHT = 700
FPS = 30
DEFAULT_SCALE_FACTOR = 0.8


class App:
    def __init__(self, points_file, n, scale_factor, fade,
                 reverse_rotation, start_paused, window_size):
        self.running = True
        self.paused = start_paused
        self.clock = None

        self.window_width, self.window_height = window_size
        display_info = pg.display.Info()
        if DEFAULT_WINDOW_WIDTH >= display_info.current_w:
            self.window_width = display_info.current_w - 200
            self.window_height = self.window_width
        if DEFAULT_WINDOW_HEIGHT >= display_info.current_h:
            self.window_height = display_info.current_h - 200
            self.window_width = self.window_height
        self.main_surface = pg.display.set_mode(
            (self.window_width, self.window_height)
        )
        pg.display.set_caption("Epicycles")

        self.epicycles = Epicycles(self.window_width, self.window_height,
                                   points_file, n, scale_factor, fade,
                                   reverse_rotation)

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
                    self.epicycles.circles_visible = not self.epicycles.circles_visible
                elif event.key in (pg.K_PLUS, pg.K_KP_PLUS):
                    self.epicycles.speed_up()
                elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                    self.epicycles.speed_down()
                elif event.key == pg.K_BACKSPACE:
                    self.epicycles.erase_line()
                elif event.key == pg.K_f:
                    self.epicycles.fade = not self.epicycles.fade
                elif event.key == pg.K_d:
                    debug_info = (
                        f"\nangle: {round(self.epicycles.angle, 2)} rad" +
                        f" ({round(math.degrees(self.epicycles.angle), 2)}°)" +
                        f"\nspeed: {self.epicycles.speed} rad/s" +
                        f"\nfps: {int(self.clock.get_fps())}"
                    )
                    print(debug_info)

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:
            dt = self.clock.tick(FPS) / 1000  # seconds
            self.handle_input()
            if not self.paused:
                self.epicycles.update(dt)
            self.epicycles.draw(self.main_surface, self.paused)
            pg.display.update()


parser = argparse.ArgumentParser()
parser.add_argument(
    "file",
    help="Path to file containing the points of the shape."
)
parser.add_argument(
    "-n",
    type=int,
    help="Maximum number of harmonics or circles.",
    metavar="<int>",
    default=None
)
parser.add_argument(
    "-s",
    "--scale_factor",
    type=float,
    metavar="<float>",
    help="A number > 0 and <= 1 indicating how much of the width and " +
         "height of the window the shape should occupy. To disable " +
         f"this set it to 0. Defaults to {DEFAULT_SCALE_FACTOR}.",
    default=DEFAULT_SCALE_FACTOR
)
parser.add_argument(
    "-f",
    "--fade",
    action="store_true",
    help="Fade the line over time so that it vanishes after one cycle."
)
parser.add_argument(
    "-r",
    "--reverse",
    action="store_true",
    help="Reverse the rotation direction of all circles."
)
parser.add_argument(
    "-p",
    "--paused",
    action="store_true",
    help="Start the app paused."
)
parser.add_argument(
    "--window_size",
    metavar=("<width>", "<height>"),
    nargs=2,
    type=int,
    help="Specify a custom window width and height in pixels.",
    default=(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
)
args = parser.parse_args()

os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()
App(
    args.file,
    args.n,
    args.scale_factor,
    args.fade,
    args.reverse,
    args.paused,
    args.window_size
).run()
