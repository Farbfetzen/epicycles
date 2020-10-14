import pygame

from src import constants
from src import scene
from src import epicycles


class Show(scene.Scene):
    def __init__(self,
                 scene_manager,
                 start_paused,
                 filename,
                 n,
                 scale,
                 fade,
                 reverse):
        super().__init__(scene_manager)
        self.paused = start_paused
        self.show_debug_overlay = False
        self.epicycles = epicycles.Epicycles(
            filename=filename,
            n=n,
            scale=scale,
            fade=fade,
            reverse=reverse,
            target_surface_rect=self.target_surface.get_rect()
        )

    def process_event(self, event):
        done = super().process_event(event)
        if done:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            # elif event.key == pygame.K_c:
            #     self.epicycles.circles_visible = not self.epicycles.circles_visible
            elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                self.epicycles.speed_up()
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.epicycles.speed_down()
            # elif event.key == pygame.K_BACKSPACE:
            #     self.epicycles.erase_line()
            # elif event.key == pygame.K_f:
            #     self.epicycles.fade = not self.epicycles.fade
            elif event.key == pygame.K_F1:
                self.show_debug_overlay = not self.show_debug_overlay

    def update(self, dt):
        if self.show_debug_overlay:
            self.update_debug_overlay()

        if self.paused:
            return
        self.epicycles.update(dt)

    def update_debug_overlay(self):
        pass

    def draw(self):
        self.target_surface.fill(constants.BACKGROUND_COLOR)
        self.epicycles.draw(self.target_surface)
        if self.show_debug_overlay:
            pass

        # DEBUG:
        r = self.target_surface.get_rect()
        pygame.draw.circle(self.target_surface, (0, 0, 255), r.center, 1)

    def start(self):
        # Only relevant when coming from the Draw scene.
        # Read the new path from the persistent data and construct new
        # epicycles accordingly.
        pass
