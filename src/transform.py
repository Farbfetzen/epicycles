import numpy.fft

import pygame

from src import constants
from src import image_loader


def complex_to_vec2(c):
    return pygame.Vector2(c.real, c.imag)


def load_txt(filename):
    with open(filename, "r") as file:
        points = []
        for line in file:
            x, y = line.split()
            # Flip the image by negating y because in pygame y=0
            # is at the top.
            points.append(pygame.Vector2(float(x), -float(y)))
    return points


def center(points):
    """Center the shape around (0, 0)"""
    max_x = max(points, key=lambda vec: vec.x).x
    min_x = min(points, key=lambda vec: vec.x).x
    max_y = max(points, key=lambda vec: vec.y).y
    min_y = min(points, key=lambda vec: vec.y).y
    shape_center = pygame.Vector2(
        (max_x + min_x) / 2,
        (max_y + min_y) / 2
    )
    for p in points:
        p -= shape_center

    width = max_x - min_x
    height = max_y - min_y

    return points, width, height


def scale(points, shape_width, shape_height, scale_factor, target_surface_rect):
    """Scale the shape relative to scale factor and window size"""
    if scale_factor < 0 or scale_factor > 1:
        raise ValueError("Argument \"--scale\" must be between 0 and 1.")

    if scale_factor != 0:
        max_allowed_width = scale_factor * target_surface_rect.width
        max_allowed_height = scale_factor * target_surface_rect.height
        if max_allowed_width <= max_allowed_height:
            ratio = max_allowed_width / shape_width
        else:
            ratio = max_allowed_height / shape_height
        for p in points:
            p *= ratio

    return points


def transform(points):
    """Calculate circles from points."""
    complex_points = [complex(*p) for p in points]
    transformed = list(numpy.fft.ifft(complex_points))
    offset = complex_to_vec2(transformed.pop(0))
    harmonics = []
    circle_radii = []
    i = 1
    increase_i = False
    sign = -1
    pop_back = False  # pop from the front or the back

    while transformed:
        radius = transformed.pop(-pop_back)
        abs_radius = abs(radius)
        # Only add harmonics over a certain radius threshold to ignore
        # harmonics which don't noticeably contribute.
        if abs_radius >= constants.HARMONICS_RADIUS_CUTOFF:
            # Save radius as complex because the accuracy of
            # numpy.complex128 is not necessary here.
            harmonics.append([complex(radius), complex(0, sign * i)])
        # Only add radius if the associated circle would be large enough
        # to be visible. Make it int because gfxdraw needs integer
        # arguments. This list is only used for drawing the circles.
        if abs_radius >= constants.CIRCLE_RADIUS_CUTOFF:
            circle_radii.append(int(abs_radius))
        if increase_i:
            i += 1
        increase_i = not increase_i
        sign *= -1
        pop_back = not pop_back

    return harmonics, circle_radii, offset


def from_txt(filename, scale_factor, target_surface_rect, n):
    points = load_txt(filename)
    points = scale(*center(points), scale_factor, target_surface_rect)
    harmonics, circle_radii, offset = transform(points)
    if n > 0:
        harmonics = harmonics[:n]
        circle_radii = circle_radii[:n]
    return harmonics, circle_radii, offset


def from_image(filename, target_surface_rect):
    # points = ...
    # return transform(points)
    pass
