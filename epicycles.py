"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""


import os
import math
import random
from pprint import pprint

import pygame as pg


os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()

DISCO_MODE = False
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_CENTER_COMPLEX = SCREEN_CENTER[0] + SCREEN_CENTER[1] * 1j
FPS = 60
BACKGROUND_COLOR = (20, 20, 20)
BACKGROUND_COLOR_TRANSP = (0, 0, 0, 0)
LINE_COLOR = [200, 200, 200]
CIRCLE_COLOR = (100, 100, 100, 128)
CIRCLE_LINE_COLOR = (255, 50, 50, 128)
CENTER_CIRCLE_RADIUS = 300

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
# a is the start position
# abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i"
# c is the position of the circle center

ab = (
    [0.1+0j, 1j],
    [0.5+0j, -1j],
    [0.1+0j, 2j]
)
# ab = (
#     [1, 1j],
#     [1/9, -3j],
#     [1/25, 5j],
#     [1/49, -7j]
# )

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
