DEFAULT_WINDOW_SIZE = (700, 700)
FPS = 60
DT_LIMIT = 2 / FPS  # max dt is twice the normal dt
DEFAULT_SCALE_FACTOR = 0.8
PATH_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
CIRCLE_COLOR = (170, 170, 170)
SPEEDS = (1/16, 1/4, 1/2, 1, 2, 3, 4)  # in radians/second

# Higher values reduce the number of points. This helps the framerate
# but reduces the resolution.
MIN_DISTANCE = 2.5  # ignore points closer than this
MAX_DISTANCE = 5  # interpolate when points are farther apart than this
