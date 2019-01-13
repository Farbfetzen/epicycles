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
# FIXME: Ditch the circle surface and the transparency stuff. Just blit
# the line surface each frame frst and then draw the circles and the circle
# lines directly on the main surface. I have to redraw them each frame anyway.


class Epicycles:
    def __init__(self, harmonics):
        self.running = True
        self.image_number = 0
        self.last_point = None
        self.t = 0
        self.paused = False
        self.circles_visible = True
        self.harmonics = harmonics

    def to_complex(self):
        pass

    def from_complex(self):
        pass

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
                    # FIXME: duplicated code:
                    c = [0 for i in range(len(self.harmonics)+1)]
                    c_complex = c.copy()
                    c[0] = SCREEN_CENTER
                    c_complex[0] = SCREEN_CENTER_COMPLEX
                    self.last_point = None
                elif event.key == pg.K_UP:
                    self.speed *= 2
                elif event.key == pg.K_DOWN:
                    self.speed = max(self.speed / 2, MIN_SPEED)
                elif event.key == pg.K_BACKSPACE:
                    line_surface.fill(BACKGROUND_COLOR)

    def update_circles(self, dt):
        self.t += speed * dt  # radians
        if self.t > math.pi * 2:
            self.t -= math.pi * 2
            # Prevent t from becoming too big.
            # This only works if the shape has a frequency of 1/(2pi).
            # That means the shape must be finished after one revolution of
            # the innermost circle. This is alway the case if the circle
            # speed follor the pattern 1, -1, 2, -2, 3, -3, ...
            if SAVE_IMAGES:
                self.running = False

        for i, k in enumerate(self.harmonics):
            p = k[0] * math.e ** (k[1] * self.t) + c_complex[i]
            c_complex[i+1] = p
            c[i+1] = (p.real, p.imag)
            pg.draw.circle(
                circle_surface,
                CIRCLE_COLOR,
                [int(f) for f in c[i]],
                max(int(abs(k[0])), 1),
                1
            )
            pg.draw.line(
                circle_surface,
                CIRCLE_LINE_COLOR,
                c[i],
                c[i+1]
            )

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
                line_surface,
                LINE_COLOR,
                self.last_point,
                c[-1],
                2
            )
        self.last_point = c[-1]

    def draw(self):
        circle_surface.fill(BACKGROUND_COLOR_TRANSP)

    def random(self):
        n = random.randint(2, 20)
        self.harmonics = []
        for i in range(n):
            a = (random.uniform(-1, 1) + random.uniform(-1, 1)*1j) / n
            a *= CENTER_CIRCLE_RADIUS
            if (i + 1) % 2 == 1:
                b = math.ceil((i + 1) / 2)
            else:
                b = (i + 1) // -2
            b = b * 1j
            self.harmonics.append([a, b])
        print("\n")
        pprint(self.harmonics)
        line_surface.fill(BACKGROUND_COLOR)

    def run(self):
        while self.running:
            dt = clock.tick(FPS) / 1000  # seconds
            self.handle_input()

            if not self.paused:
                self.update_circles(dt)

            main_surface.blit(line_surface, (0, 0))
            if self.circles_visible:
                main_surface.blit(circle_surface, (0, 0))
            pg.display.update()

            pressed = pg.key.get_pressed()
            if pressed[pg.K_s] or SAVE_IMAGES:
                self.image_number += 1
                pg.image.save(
                    main_surface,
                    "screenshots/" + str(self.image_number).zfill(5) + ".png"
                )
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


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pg.init()


DISCO_MODE = False
SAVE_IMAGES = False
SCREEN_WIDTH = 900  # 600 or less for gifs and videos
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_CENTER_COMPLEX = SCREEN_CENTER[0] + SCREEN_CENTER[1] * 1j
FPS = 25 if SAVE_IMAGES else 60
BACKGROUND_COLOR = (255, 255, 255)
BACKGROUND_COLOR_TRANSP = (255, 255, 255, 0)
LINE_COLOR = [0, 0, 0]
CIRCLE_COLOR = (128, 128, 128)
CIRCLE_LINE_COLOR = (255, 0, 0)
CENTER_CIRCLE_RADIUS = 50  # Adjust manually for different shapes

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Epicycles")
line_surface = main_surface.copy()
circle_surface = main_surface.convert_alpha()
line_surface.fill(BACKGROUND_COLOR)
clock = pg.time.Clock()
speed = 1  # speed of the innermost circle in radians/second
MIN_SPEED = 1/16


# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i"
# c is the position of the circle center

# harmonics = (
#     [1, 1j],
#     [1/9, -3j],
#     [1/25, 5j],
#     [1/49, -7j]
# )
# harmonics = (
#     [1, 1j],
#     [1/3, 3j],
#     [1/5, 5j],
#     [1/7, 7j],
#     [1/9, 9j]
# )



for k in self.harmonics:
    k[0] *= CENTER_CIRCLE_RADIUS
c = [0 for i in range(len(self.harmonics)+1)]
c_complex = c.copy()
c[0] = SCREEN_CENTER
c_complex[0] = SCREEN_CENTER_COMPLEX


