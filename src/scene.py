import pygame

from src import constants


class Scene:
    def __init__(self, scene_manager, debug):
        self.scene_manager = scene_manager
        self.target_surface = scene_manager.display
        self.debug_mode = debug

        self.debug_font = pygame.freetype.SysFont(
            "consolas, inconsolate, monospace",
            16
        )
        self.debug_font.pad = True
        self.debug_font.fgcolor = [(255 - c) % 256 for c in constants.BACKGROUND_COLOR[:3]]
        self.debug_line_spacing = pygame.Vector2(
            0, self.debug_font.get_sized_height()
        )
        self.debug_margin = pygame.Vector2(5, 5)

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.close()
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            elif event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode

    def update(self, dt):
        pass

    def draw(self):
        pass

    def start(self):
        self.debug_mode = self.scene_manager.persistent_scene_data.get(
            "debug_mode", self.debug_mode
        )

    def close(self, next_scene_name=""):
        self.scene_manager.persistent_scene_data["debug_mode"] = self.debug_mode
        self.scene_manager.change_scenes(next_scene_name)
