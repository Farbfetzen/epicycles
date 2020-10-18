import pygame


class Scene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.target_surface = scene_manager.display

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.close()
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True

    def update(self, dt):
        pass

    def draw(self):
        pass

    def start(self):
        pass

    def close(self, next_scene_name=""):
        self.scene_manager.change_scenes(next_scene_name)
