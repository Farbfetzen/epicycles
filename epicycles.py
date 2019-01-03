"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""

# TODO:
# - Make radius a float to allow for very small circles.
# - Use complex numbers.
# - When drawing very small circles either draw them with radius=1 or don't draw them.
# - Calculate the parameters of the circles for a path using fourier analysis.
# - Read in images?
# - Use command line arguments.


import os
from math import pi, sin, cos

import pygame as pg


os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
FPS = 60
LINE_COLOR = (255, 255, 255)
CIRCLE_COLOR = (200, 200, 200, 75)
DRAW_POINT_RADIUS = 3


class Circle:
    def __init__(self, radius, angle, speed,
                 parent=None, clockwise=True, draw_line=False):
        # TODO: Find better name for variable foo. That is the point on a
        #    circle where either the center of the child circle is attached
        #    or where the point for drawing the line is.

        self.radius = int(round(radius))  # pixel
        self.angle = angle  # radians
        self.speed = speed  # radians per second
        self.parent = parent
        self.direction = -1 if clockwise else 1
        self.draw_line = draw_line
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.foo = [0, 0]
        self.last_point = self.foo
        if parent is not None:
            self.set_parent(parent)
        self.update(0)  # initialize self.foo and self.last_point

    def set_parent(self, parent):
        self.parent = parent
        self.center = self.parent.foo
        self.update(0)

    def update(self, dt):
        if self.parent is not None:
            self.center = self.parent.foo
        self.angle += self.speed * dt * self.direction
        if self.angle > pi * 2:
            self.angle -= pi * 2
        self.last_point = [int(p) for p in self.foo]
        self.foo = [self.center[0] + cos(self.angle) * self.radius,
                    self.center[1] - sin(self.angle) * self.radius]

    def draw(self):
        foo_int = [int(p) for p in self.foo]
        center_int = [int(p) for p in self.center]
        pg.draw.circle(circle_surface, CIRCLE_COLOR, center_int,
                       self.radius, 1)
        pg.draw.line(circle_surface, CIRCLE_COLOR, center_int, foo_int)
        if self.draw_line:
            pg.draw.line(line_surface, LINE_COLOR, self.last_point,
                         foo_int)


# circles = [
#     Circle(300, 0, 1),
#     Circle(300/2, 0, 2, clockwise = False)
# ]

# square:
circles = [
    Circle(300, pi/4, 1),
    Circle(300/3**2, pi/4, 3, clockwise=False),
    Circle(300/5**2, pi/4, 5),
    Circle(300/7**2, pi/4, 7, clockwise=False),
]

# triangle:
# circles = [
#     Circle(300, 0, 1),
#     Circle(300/4, pi, 2, clockwise=False),
#     Circle(300/16, 0, 4)
# ]

for i in range(1, len(circles)):
    circles[i].set_parent(circles[i-1])

circles[-1].draw_line = True
paused = False
circles_visible = True

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
line_surface = main_surface.copy()
circle_surface = main_surface.convert_alpha()
clock = pg.time.Clock()

running = True
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

    if not paused:
        circle_surface.fill((0, 0, 0, 0))
        for c in circles:
            c.update(dt)
            c.draw()

    main_surface.blit(line_surface, (0, 0))
    if circles_visible:
        main_surface.blit(circle_surface, (0, 0))
    pg.display.update()
