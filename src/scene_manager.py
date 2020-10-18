import pygame
import pygame.freetype

from src import constants
from src import scene_circles
from src import scene_draw


class SceneManager:
    def __init__(self, file, n, scale, fade,
                 reverse, start_paused, window_size, debug):
        pygame.init()
        pygame.display.set_caption("Epicycles")
        self.display = pygame.display.set_mode(window_size)
        self.running = True
        self.clock = pygame.time.Clock()

        self.scenes = {
            "circles": scene_circles.Circles(self, start_paused, debug),
            "draw": scene_draw.Draw(self, debug)
        }
        self.persistent_scene_data = {}
        if file:
            self.active_scene = self.scenes["circles"]
            self.active_scene.start(filename=file, n=n, scale=scale,
                                    fade=fade, reverse=reverse)
        else:
            self.active_scene = self.scenes["draw"]

    def run(self):
        # Prevent the first dt from getting too large due to file loading etc.
        self.clock.tick()

        while self.running:
            # Protect against hiccups (e.g. from moving the pygame window)
            # by setting an upper limit to dt.
            dt = min(self.clock.tick(constants.FPS) / 1000, constants.DT_LIMIT)
            for event in pygame.event.get():
                self.active_scene.process_event(event)
            self.active_scene.update(dt)
            self.active_scene.draw()
            pygame.display.flip()

    def change_scenes(self, next_scene_name):
        if next_scene_name == "":
            self.running = False
            return
        self.active_scene = self.scenes[next_scene_name]
        self.active_scene.start()
