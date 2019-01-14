"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""


import os
import math
import random
from pprint import pprint

import pygame as pg


# TODO: Try to automatically adjust the size of the center circle. Make sure
# that the sum of the radii of all circles is less than half of the window
# width minus a small border.
# TODO: Load harmonics from file if given a filename. Modify the file format
# outputtet by the R script, i.e. remove the brackets and trailing commas.

# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i" in math and physics
# c is the position of the circle center

DISCO_MODE = False
SAVE_IMAGES = False
SCREEN_WIDTH = 900  # 600 or less for gifs and videos
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
FPS = 25 if SAVE_IMAGES else 60
BACKGROUND_COLOR = (255, 255, 255)
LINE_COLOR = [0, 0, 0]
CIRCLE_COLOR = (128, 128, 128)
CIRCLE_LINE_COLOR = (255, 0, 0)
CENTER_CIRCLE_RADIUS = 400  # Adjust manually for different shapes
MIN_SPEED = 1/16
EXAMPLE_DIAMOND = [
    [1, 1j],
    [1/9, -3j],
    [1/25, 5j],
    [1/49, -7j]
]
EXAMPLE_SQUARE_WAVE = [
    [1, 1j],
    [1/3, 3j],
    [1/5, 5j],
    [1/7, 7j],
    [1/9, 9j]
]
EXAMPLE_STAR = [
    [0.5447818+0.1770103j, 2j],
    [0.2421415+0.0786765j, -3j],
    [0.0444989+0.0144586j, 7j],
    [0.0340763+0.0110721j, -8j]
]

class Epicycles:
    def __init__(self, harmonics):
        self.harmonics = harmonics
        for i, h in enumerate(self.harmonics):
            # Invert y-axis for pygame window.
            z = h[0]
            self.harmonics[i][0] = complex(z.real, z.imag * -1)
        self.running = True
        self.image_number = 0
        self.last_point = None
        self.t = 0  # radians
        self.paused = False
        self.circles_visible = True
        self.speed = 1  # speed of the innermost circle in radians/second
        self.main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.line_surface = self.main_surface.copy()
        self.line_surface.fill(BACKGROUND_COLOR)
        pg.display.set_caption("Epicycles")

        for i in range(len(self.harmonics)):
            self.harmonics[i][0] *= CENTER_CIRCLE_RADIUS
        self.circle_points = [0 for i in range(len(self.harmonics)+1)]
        self.circle_points_complex = self.circle_points.copy()
        self.circle_points[0] = SCREEN_CENTER
        self.circle_points_complex[0] = self.to_complex(SCREEN_CENTER)

    @staticmethod
    def to_complex(xy):
        return complex(xy[0], xy[1])

    @staticmethod
    def from_complex(z):
        return [z.real, z.imag]

    def random(self):
        # TODO: Scale the random circle radii so that the result fits on the
        # screen and is not too small.
        n = random.randint(2, 20)
        self.harmonics = []
        for i in range(n):
            a = complex(random.uniform(-1, 1), random.uniform(-1, 1)) / n
            a *= CENTER_CIRCLE_RADIUS
            if (i + 1) % 2 == 1:
                b = math.ceil((i + 1) / 2)
            else:
                b = (i + 1) // -2
            b = complex(0, b)
            self.harmonics.append([a, b])
        print("\n")
        pprint(self.harmonics)
        self.line_surface.fill(BACKGROUND_COLOR)

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
                elif event.key == pg.K_r:
                    self.random()
                    # FIXME: refactor duplicated code:
                    self.circle_points = [0 for i in range(len(self.harmonics)+1)]
                    self.circle_points_complex = self.circle_points.copy()
                    self.circle_points[0] = SCREEN_CENTER
                    self.circle_points_complex[0] = self.to_complex(SCREEN_CENTER)
                    self.last_point = None
                elif event.key == pg.K_UP:
                    self.speed *= 2
                elif event.key == pg.K_DOWN:
                    self.speed = max(self.speed / 2, MIN_SPEED)
                elif event.key == pg.K_BACKSPACE:
                    self.line_surface.fill(BACKGROUND_COLOR)

    def update_circles(self, dt):
        self.t += self.speed * dt  # radians
        if self.t > math.pi * 2:
            self.t -= math.pi * 2
            # Prevent t from becoming too big.
            # This only works if the shape has a frequency of 1/(2pi).
            # That means the shape must be finished after one revolution of
            # the innermost circle. This is alway the case if the circle
            # speed follor the pattern 1, -1, 2, -2, 3, -3, ...
            if SAVE_IMAGES:
                self.running = False

        for i, h in enumerate(self.harmonics):
            p = h[0] * math.e ** (h[1] * self.t) + self.circle_points_complex[i]
            self.circle_points_complex[i+1] = p
            self.circle_points[i+1] = self.from_complex(p)

    def draw(self):
        if self.last_point is not None:
            if DISCO_MODE:
                for i in range(len(LINE_COLOR)):
                    LINE_COLOR[i] = max(
                        min(
                            LINE_COLOR[i] + random.choice((-20, 0, 20)),
                            255
                        ),
                        0
                    )
            pg.draw.line(
                self.line_surface,
                LINE_COLOR,
                self.last_point,
                self.circle_points[-1],
                2
            )

        self.main_surface.blit(self.line_surface, (0, 0))
        if self.circles_visible:
            for i, k in enumerate(self.harmonics):
                pg.draw.circle(
                    self.main_surface,
                    CIRCLE_COLOR,
                    [int(f) for f in self.circle_points[i]],
                    max(int(abs(k[0])), 1),
                    1
                )
                pg.draw.line(
                    self.main_surface,
                    CIRCLE_LINE_COLOR,
                    self.circle_points[i],
                    self.circle_points[i+1]
                )

    def run(self):
        dt = 0
        clock = pg.time.Clock()

        while self.running:
            dt = clock.tick(FPS) / 1000  # seconds
            self.handle_input()
            if not self.paused:
                self.update_circles(dt)
            self.draw()
            self.last_point = self.circle_points[-1]
            pg.display.update()

            if SAVE_IMAGES:
                self.image_number += 1
                pg.image.save(
                    self.main_surface,
                    "screenshots/" + str(self.image_number).zfill(5) + ".png"
                )


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pg.init()
    Epicycles(EXAMPLE_STAR).run()


# How to make an animated gif with gimp because I don't
# understand how to make small gifs with imagemagick:
# 1. load all images in gimp with file > open as layers
# 2. image > mode > indexed: 255 colors
# 3. filters > animation > optimize for gif
# 4. file > export as: "filename.gif", delay = 1000/fps,
#    no gif comment, use delay for all frames
# Experiment with maybe removing the first frames for a better loop.
#
# Alternatively there is this way with imagemagick:
# cd screenshots
# convert -delay 4 -loop 0 -layers optimize *.png animation.gif
# The "4" after "-delay" is 100/fps.
# But the filesize is still larger than with gimp and I don't know why.
#
# Either way the file size can be further reduced by converting the
# animated gif to a mp4 or webm using ffmpeg.
# Example taken from https://unix.stackexchange.com/a/294892
# ffmpeg -i animated.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" video.mp4
