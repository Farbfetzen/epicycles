DEFAULT_WINDOW_SIZE = (700, 700)
FPS = 30
DEFAULT_SCALE_FACTOR = 0.8

PATH_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
CIRCLE_COLOR = (170, 170, 170)
CIRCLE_LINE_COLOR = (60, 60, 60)
CIRCLE_LINE_THICKNESS = 1
PATH_LINE_THICKNESS = 3
SMOOTH_SCALE_FACTOR = 1.5  # < 2 for performance but > 1 for nice looking result
# Max. distance between two points before interpolation kicks in:
MAX_DIST = 5 * SMOOTH_SCALE_FACTOR
MIN_SPEED = 1/16
MAX_SPEED = 4
# TODO: Use a constant speed list and a speed index.
