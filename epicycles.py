"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""

# TODO: Switch the order of the surfaces. Draw the circles behind the line.
#       This includes making the circle surface opaque and the line surface
#       transparent.


import os
import math
import random
from pprint import pprint

import pygame as pg


os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()

DISCO_MODE = False
SAVE_IMAGES = False
SCREEN_WIDTH = 900  # 600 or less for gifs and videos
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_CENTER_COMPLEX = SCREEN_CENTER[0] + SCREEN_CENTER[1] * 1j
FPS = 25 if SAVE_IMAGES else 60
BACKGROUND_COLOR = (20, 20, 20)
BACKGROUND_COLOR_TRANSP = (0, 0, 0, 0)
LINE_COLOR = [255, 125, 0]
CIRCLE_COLOR = (100, 100, 100)
CIRCLE_LINE_COLOR = (200, 50, 50)
CENTER_CIRCLE_RADIUS = 200  # 150 for gifs and videos

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Epicycles")
line_surface = main_surface.copy()
circle_surface = main_surface.convert_alpha()
line_surface.fill(BACKGROUND_COLOR)
clock = pg.time.Clock()
speed = 1  # speed of the innermost circle in radians/second
paused = False
circles_visible = True
running = True
t = 0

# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i"
# c is the position of the circle center

# ab = (
#     [1, 1j],
#     [1/9, -3j],
#     [1/25, 5j],
#     [1/49, -7j]
# )

ab = (
    [1, 1j],
    [1/3, 3j],
    [1/5, 5j],
    [1/7, 7j],
    [1/9, 9j]
)

# H:
ab = (
    [-1.1824635-0.7900968j, 1j],
    [-0.0872584+0.0583042j, -1j],
    [0+0j, 2j],
    [0+0j, -2j],
    [0.0786277-0.3952883j, 3j],
    [-0.0624539-0.3139772j, -3j],
    [0+0j, 4j],
    [0+0j, -4j],
    [-0.1072115+0.0213257j, 5j],
    [0.0634019+0.0126114j, -5j],
    [0+0j, 6j],
    [0+0j, -6j],
    [-0.0450106-0.0673631j, 7j],
    [-0.0420398+0.0629169j, -7j],
    [0+0j, 8j],
    [0+0j, -8j],
    [-0.0254325+0.0380625j, 9j],
    [-0.0272298-0.0407523j, -9j],
    [0+0j, 10j],
    [0+0j, -10j],
)

def new_random():
    n = random.randint(2, 20)
    ab = []
    for i in range(n):
        a = (random.uniform(-1, 1) + random.uniform(-1, 1)*1j) / n
        a *= CENTER_CIRCLE_RADIUS
        if (i + 1) % 2 == 1:
            b = math.ceil((i + 1) / 2)
        else:
            b = (i + 1) // -2
        b = b * 1j
        ab.append([a, b])
    print("\n")
    pprint(ab)
    line_surface.fill(BACKGROUND_COLOR)
    return ab

for k in ab:
    k[0] *= CENTER_CIRCLE_RADIUS
c = [0 for i in range(len(ab)+1)]
c_complex = c.copy()
c[0] = SCREEN_CENTER
c_complex[0] = SCREEN_CENTER_COMPLEX
last_point = None
image_number = 1

while running:
    dt = clock.tick(FPS) / 1000  # seconds

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_p or event.key == pg.K_SPACE:
                paused = not paused
            elif event.key == pg.K_c:
                circles_visible = not circles_visible
            elif event.key == pg.K_r:
                ab = new_random()
                # FIXME: duplicated code:
                c = [0 for i in range(len(ab)+1)]
                c_complex = c.copy()
                c[0] = SCREEN_CENTER
                c_complex[0] = SCREEN_CENTER_COMPLEX
                last_point = None
            elif event.key == pg.K_UP:
                speed += 0.5
            elif event.key == pg.K_DOWN:
                speed = max(speed - 0.5, 0.5)
            elif event.key == pg.K_BACKSPACE:
                line_surface.fill(BACKGROUND_COLOR)

    if not paused:
        circle_surface.fill(BACKGROUND_COLOR_TRANSP)

        t += speed * dt
        if t > math.pi * 2:
            t -= math.pi * 2
            # Prevent t from becoming too big.
            # This only works if the shape has a frequency of 1/(2pi).
            # That means the shape must be finished after one revolution of
            # the innermost circle. This is alway the case if the circle
            # speed follor the pattern 1, -1, 2, -2, 3, -3, ...
            if SAVE_IMAGES:
                running = False

        for i, k in enumerate(ab):
            p = k[0] * math.e ** (k[1] * t) + c_complex[i]
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

        if last_point is not None:
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
                last_point,
                c[-1],
                2
            )
        last_point = c[-1]

    main_surface.blit(line_surface, (0, 0))
    if circles_visible:
        main_surface.blit(circle_surface, (0, 0))
    pg.display.update()

    pressed = pg.key.get_pressed()
    if pressed[pg.K_s] or SAVE_IMAGES:
        pg.image.save(
            main_surface,
            "screenshots/" + str(image_number).zfill(5) + ".png"
        )
        image_number += 1
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
