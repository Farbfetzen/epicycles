"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""


import os
import math

import pygame as pg


os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_CENTER_COMPLEX = SCREEN_CENTER[0] + SCREEN_CENTER[1] * 1j
FPS = 60
BACKGROUND_COLOR = (255, 255, 255)
BACKGROUND_COLOR_TRANSP = (255, 255, 255, 0)
LINE_COLOR = (0, 0, 0)
CIRCLE_COLOR = (180, 180, 255)
SPEED = 1  # speed of the innermost circle in radians/second
CENTER_CIRCLE_RADIUS = 300

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
line_surface = main_surface.copy()
circle_surface = main_surface.convert_alpha()
line_surface.fill(BACKGROUND_COLOR)
clock = pg.time.Clock()
paused = False
circles_visible = True
running = True
t = 0

# This is the formula:
# a * exp(bj * t) + c
# a is the start position
# abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# c is the position of the circle center

ab = (
    [0.1+0j, 1j],
    [0.5+0j, -2.5j],
    [0.1+0j, 1j]
)
# ab = (
#     [1, 1j],
#     [1/9, -3j],
#     [1/25, 5j],
#     [1/49, -7j]
# )
for k in ab:
    k[0] *= CENTER_CIRCLE_RADIUS
c = [0 for i in range(len(ab)+1)]
c_complex = c.copy()
c[0] = SCREEN_CENTER
c_complex[0] = SCREEN_CENTER_COMPLEX

# Get the first point:
for i, k in enumerate(ab):
    p = k[0] * math.e ** (k[1] * t) + c_complex[i]
    c_complex[i+1] = p
    c[i+1] = [p.real, p.imag]
last_point = c[-1]
# Prevent a pixel artifact that sometimes appears:
last_point[0] -= 0.001
last_point[1] -= 0.001

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
            elif event.key == pg.K_RETURN:
                print(t)
                print(c1)

    if not paused:
        circle_surface.fill(BACKGROUND_COLOR_TRANSP)

        t += SPEED * dt
        # if t > math.pi * 2:
        #     t -= math.pi * 2

        for i, k in enumerate(ab):
            p = k[0] * math.e ** (k[1] * t) + c_complex[i]
            c_complex[i+1] = p
            c[i+1] = (p.real, p.imag)
            pg.draw.circle(
                circle_surface,
                CIRCLE_COLOR,
                [int(f) for f in c[i]],
                int(abs(k[0])),
                1
            )
            pg.draw.line(
                circle_surface,
                CIRCLE_COLOR,
                c[i],
                c[i+1]
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
