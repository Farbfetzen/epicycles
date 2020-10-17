DEFAULT_WINDOW_SIZE = (700, 700)
FPS = 60
DT_LIMIT = 2 / FPS  # max dt is twice the normal dt
DEFAULT_SCALE_FACTOR = 0.8
PATH_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 255, 255)
CIRCLE_COLOR = (170, 170, 170)
DEFAULT_ANGULAR_VELOCITY = 1  # in radians/second
MIN_ANGULAR_VELOCITY = 1 / 32
MAX_ANGULAR_VELOCITY = 4

# The numbers in this section control the resolution but impact performance.
# Smaller numbers result in prettier visuals but larger numbers make
# the app run smoother.
MIN_DISTANCE = 2.5  # ignore point if it is closer than this to previous point
MAX_DISTANCE = 5  # interpolate when points are farther apart than this
CIRCLE_RADIUS_CUTOFF = 1  # circles with smaller radii will not be drawn
HARMONICS_RADIUS_CUTOFF = 0.01  # harmonics with smaller radii will be ignored
