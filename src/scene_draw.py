import pygame

from src import scene
from src import constants
from src import transform


class Draw(scene.Scene):
    def __init__(self, scene_manager, debug):
        super().__init__(scene_manager, debug)
        self.points = []

    def process_event(self, event):
        done = super().process_event(event)
        if done:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.close("circles")
            elif event.key == pygame.K_BACKSPACE:
                self.points = []

    def update(self, dt):
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos not in self.points:
                self.points.append(mouse_pos)

    def draw(self):
        self.target_surface.fill(constants.BACKGROUND_COLOR)
        if len(self.points) > 1:
            pygame.draw.aalines(
                self.target_surface,
                constants.DRAW_COLOR,
                False,
                self.points
            )

        if self.debug_mode:
            fps = int(self.scene_manager.clock.get_fps())
            self.debug_font.render_to(
                self.target_surface,
                self.debug_margin,
                f"fps: {fps}"
            )

    def close(self, next_scene_name=""):
        if len(self.points) > 1:
            points = [pygame.Vector2(p) for p in self.points]
            points = transform.center(points)[0]
            self.scene_manager.persistent_scene_data["points"] = points
        super().close(next_scene_name)
