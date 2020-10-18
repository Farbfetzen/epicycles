import pygame
import pygame.freetype

import math

from src import constants
from src import scene
from src import epicycles
from src import transform


class Circles(scene.Scene):
    def __init__(self, scene_manager, start_paused, debug):
        super().__init__(scene_manager)
        self.paused = start_paused
        self.debug_mode = debug
        self.epicycles = None
        self.debug_font = pygame.freetype.SysFont(
            "consolas, inconsolate, monospace",
            18
        )
        self.debug_font.pad = True
        self.debug_font.fgcolor = [(255 - c) % 256 for c in constants.BACKGROUND_COLOR[:3]]
        self.debug_line_spacing = pygame.Vector2(
            0, self.debug_font.get_sized_height()
        )
        self.debug_margin = pygame.Vector2(5, 5)

    def process_event(self, event):
        done = super().process_event(event)
        if done:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_c:
                self.epicycles.circles_visible = not self.epicycles.circles_visible
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                self.epicycles.rotate_faster()
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                self.epicycles.rotate_slower()
            elif event.key == pygame.K_r:
                self.epicycles.reverse_direction()
            elif event.key == pygame.K_BACKSPACE:
                self.epicycles.erase_line()
            elif event.key == pygame.K_f:
                self.epicycles.fade = not self.epicycles.fade
            elif event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode

    def update(self, dt):
        if not self.paused:
            self.epicycles.update(dt)

    def draw(self):
        self.target_surface.fill(constants.BACKGROUND_COLOR)
        self.epicycles.draw(self.target_surface)

        if self.debug_mode:
            fps = int(self.scene_manager.clock.get_fps())
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin,
                f"fps: {fps}"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing,
                f"angular velocity: {self.epicycles.angular_velocity} rad/s"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing * 2,
                f"angle: {self.epicycles.current_angle:.2f} rad " +
                f"({self.epicycles.current_angle % math.tau:.2f})"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing * 3,
                f"oldest angle: {self.epicycles.angles[0]:.2f} rad " +
                f"({self.epicycles.angles[0] % math.tau:.2f})"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing * 4,
                f"number of points: {len(self.epicycles.points)}"
            )

    def start(self, filename="", points=None, n=0, fade=False,
              scale=constants.DEFAULT_SCALE_FACTOR, reverse=False):
        target_surface_rect = self.target_surface.get_rect()
        if filename:
            with open(filename, "r") as file:
                points = []
                for line in file:
                    x, y = line.split()
                    # Flip the image by negating y because in pygame y=0
                    # is at the top.
                    points.append(pygame.Vector2(float(x), -float(y)))
            points = transform.scale(
                *transform.center(points),
                scale,
                target_surface_rect
            )

        self.epicycles = epicycles.Epicycles(
            points=points,
            n=n,
            fade=fade,
            reverse=reverse,
            surface_center=target_surface_rect.center,
            debug=self.debug_mode
        )
