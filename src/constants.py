import pygame


DEFAULT_WINDOW_SIZE = (700, 700)
FPS = 60
DT_LIMIT = 2 / FPS  # max dt is twice the normal dt
DEFAULT_SCALE_FACTOR = 0.8
LINE_COLOR = pygame.Color(0, 255, 255)
BACKGROUND_COLOR = pygame.Color(32, 32, 32)
CIRCLE_COLOR = pygame.Color(128, 128, 128)
DEFAULT_ANGULAR_VELOCITY = 1  # in radians/second
MIN_ANGULAR_VELOCITY = 1 / 32
MAX_ANGULAR_VELOCITY = 4

# The numbers in this section control the resolution but impact performance.
# Smaller numbers result in prettier visuals but larger numbers make
# the app run smoother.
# Distances are squared to avoid calculating square roots.
MIN_DISTANCE_SQ = 2.5 ** 2  # ignore point if it is closer than this to previous point
MAX_DISTANCE_SQ = 5 ** 2  # interpolate when points are farther apart than this
CIRCLE_RADIUS_CUTOFF = 1  # circles with smaller radii will not be drawn
HARMONICS_RADIUS_CUTOFF = 0.01  # harmonics with smaller radii will be ignored
