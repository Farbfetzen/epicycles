import pygame
import pygame.freetype

from src import constants
from src import scene
from src import epicycles


class Circles(scene.Scene):
    def __init__(self, scene_manager, start_paused, filename, n,
                 scale, fade, reverse, debug):
        super().__init__(scene_manager)
        self.paused = start_paused
        self.debug_mode = debug
        self.epicycles = epicycles.Epicycles(
            filename=filename,
            n=n,
            scale=scale,
            fade=fade,
            reverse=reverse,
            target_surface_rect=self.target_surface.get_rect()
        )
        self.debug_font = pygame.freetype.SysFont(
            "consolas, inconsolate, monospace",
            18
        )
        self.debug_font.pad = True
        # Text color is inverted background color:
        self.debug_font.fgcolor = [(255 - c) % 256 for c in constants.BACKGROUND_COLOR]
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
            # elif event.key == pygame.K_f:
            #     self.epicycles.fade = not self.epicycles.fade
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
                f"angle: {self.epicycles.angles[-1]:.2f} rad"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing * 3,
                f"oldest angle: {self.epicycles.angles[0]:.2f} rad"
            )
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin + self.debug_line_spacing * 4,
                f"number of points: {len(self.epicycles.points)}"
            )

    def start(self):
        # Only relevant when coming from the Draw scene.
        # Read the new path from the persistent data and construct new
        # epicycles accordingly.
        pass
