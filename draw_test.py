"""This script is just for figuring out stuff."""


import math
import os
import pygame as pg


WIDTH = 500
HEIGHT = 400
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
RADIUS = 300
MAX_DIST = 50

os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()
window = pg.display.set_mode((WIDTH, HEIGHT))
window.fill(BG_COLOR)


def get_point(angle):
    x = math.cos(angle) * RADIUS
    y = math.sin(angle) * RADIUS
    return x, y


def get_dist(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.hypot(dx, dy)

count = []

def interpolate(p1, p2, a1, a2):
    count.append(1)
    mean_angle = (a1 + a2) / 2
    new_point = get_point(mean_angle)
    result = []
    if get_dist(p1, new_point) > MAX_DIST:
        interp_1 = interpolate(p1, new_point, a1, mean_angle)
    else:
        interp_1 = ()
    result.append(new_point)
    if get_dist(new_point, p2) > MAX_DIST:
        interp_2 = interpolate(new_point, p2, mean_angle, a2)
    else:
        interp_2 = ()
    result = (*interp_1, new_point, *interp_2)
    return result

previous_angle = 0
previous_point = get_point(previous_angle)
angle = math.pi / 2
point = get_point(angle)
print(previous_point)
print(point)

foo = interpolate(previous_point, point, previous_angle, angle)
foo = (previous_point, *foo, point)
#print(foo)

pg.draw.line(window, LINE_COLOR, previous_point, point)
pg.draw.lines(window, LINE_COLOR, False, foo)

for p in foo:
    pg.draw.circle(window, LINE_COLOR, [int(i) for i in p], 3, 1)

print(sum(count))

pg.display.update()

running = True
while running:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False
        elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            running = False
            
