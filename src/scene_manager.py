import pygame
import pygame.freetype

from src import constants
from src import show_scene


class SceneManager:
    def __init__(self, file, n, scale, fade,
                 reverse, start_paused, window_size):
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Epicycles")

        # TODO: Make it possible to start the game without a filename, thus
        #  making the first scene "Draw".

        self.scenes = {
            "show": show_scene.Show(
                self,
                start_paused,
                file,
                n,
                scale,
                fade,
                reverse
            )
        }
        self.persistent_scene_data = {}
        self.active_scene = self.scenes["show"]
        self.active_scene.start()

    def run(self):
        while self.running:
            # Protect against hiccups (e.g. from moving the pygame window)
            # by limiting to 100 milliseconds.
            dt = min(self.clock.tick(constants.FPS), 100) / 1000
            for event in pygame.event.get():
                self.active_scene.process_event(event)
            self.active_scene.update(dt)
            self.active_scene.draw()
            pygame.display.flip()

    def change_scenes(self, next_scene_name):
        # TODO: Make a scene where the user can draw their own shapes. Then
        #  pass that pointlist to the Show scene.
        if next_scene_name == "":
            if __name__ == '__main__':
                self.running = False
                return
        self.active_scene = self.scenes[next_scene_name]
        self.active_scene.start()
