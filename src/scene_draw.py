import pygame

from src import scene
from src import constants


class Draw(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)

    def process_event(self, event):
        done = super().process_event(event)
        if done:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.close()

    def update(self, dt):
        pass

    def draw(self):
        pass
