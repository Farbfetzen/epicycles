"""Sebastian Henz (2018)
License: MIT (see file LICENSE for details)
"""

# TODO: Switch the order of the surfaces. Draw the circles behind the line.
#       This includes making the circle surface opaque and the line surface
#       transparent.


import os
import math
import random
from pprint import pprint

import pygame as pg


os.environ["SDL_VIDEO_CENTERED"] = "1"
pg.init()

DISCO_MODE = False
SAVE_IMAGES = False
SCREEN_WIDTH = 900  # 600 or less for gifs and videos
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_CENTER_COMPLEX = SCREEN_CENTER[0] + SCREEN_CENTER[1] * 1j
FPS = 25 if SAVE_IMAGES else 60
BACKGROUND_COLOR = (255, 255, 255)
BACKGROUND_COLOR_TRANSP = (255, 255, 255, 0)
LINE_COLOR = [0, 0, 0]
CIRCLE_COLOR = (128, 128, 128)
CIRCLE_LINE_COLOR = (255, 0, 0)
CENTER_CIRCLE_RADIUS = 50  # Adjust manually for different shapes

main_surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Epicycles")
line_surface = main_surface.copy()
circle_surface = main_surface.convert_alpha()
line_surface.fill(BACKGROUND_COLOR)
clock = pg.time.Clock()
speed = 1  # speed of the innermost circle in radians/second
MIN_SPEED = 1/16
paused = False
circles_visible = True
running = True
t = 0

# This is the formula:
# a * exp(bj * t) + c
# a is the start position, abs(a) is the circle radius
# b is the speed and direction of the rotation (negative values rotate anticlockwise)
# j is sqrt(-1), usually denoted "i"
# c is the position of the circle center

# ab = (
#     [1, 1j],
#     [1/9, -3j],
#     [1/25, 5j],
#     [1/49, -7j]
# )
# ab = (
#     [1, 1j],
#     [1/3, 3j],
#     [1/5, 5j],
#     [1/7, 7j],
#     [1/9, 9j]
# )

# Transferred from R output:
ab = (
    [0.0053377-0.4349346j, 1j],
    [-0.0709597-5.7820232j, -1j],
    [-0.0517527+1.4050933j, 3j],
    [-0.0699673-1.8996247j, -3j],
    [0.0171596-0.2793077j, 5j],
    [0.0405212+0.6595643j, -5j],
    [-0.0605164+0.7027404j, 7j],
    [0.03467+0.4026015j, -7j],
    [0.0717506-0.6469966j, 9j],
    [-0.0169153-0.15253j, -9j],
    [0.0127831-0.0941207j, 11j],
    [0.0497368+0.3662061j, -11j],
    [0.0205527-0.1277345j, 13j],
    [-0.1054507-0.6553747j, -13j],
    [-0.0167812+0.0901317j, 15j],
    [-0.0831457-0.446575j, -15j],
    [0.0663407-0.313369j, 17j],
    [0.0255065+0.1204833j, -17j],
    [0.0622429-0.2620925j, 19j],
    [0.0097989+0.0412613j, -19j],
    [-0.0112216+0.0425756j, 21j],
    [-0.0191235-0.0725558j, -21j],
    [0.0308828-0.1064944j, 23j],
    [0.0039446+0.0136023j, -23j],
    [-0.0211933+0.0668984j, 25j],
    [-0.0333105-0.1051474j, -25j],
    [0.0338651-0.0984387j, 27j],
    [-0.0086613-0.0251767j, -27j],
    [-0.0838957+0.2257017j, 29j],
    [-0.0339557-0.09135j, -29j],
    [-0.0859839+0.2150091j, 31j],
    [-0.008273-0.0206872j, -31j],
    [0.0551991-0.1287697j, 33j],
    [-0.0668556-0.1559624j, -33j],
    [0.036233-0.0791056j, 35j],
    [-0.0840132-0.1834215j, -35j],
    [-0.0309191+0.0633497j, 37j],
    [0.0175918+0.0360437j, -37j],
    [-0.0073901+0.0142436j, 39j],
    [-0.0397334-0.0765819j, -39j],
    [-0.0210227+0.0381957j, 41j],
    [0.0241489+0.0438757j, -41j],
    [-0.003816+0.0065475j, 43j],
    [-0.022549-0.0386897j, -43j],
    [-0.044418+0.0720858j, 45j],
    [0.0475104+0.0771045j, -45j],
    [-0.0402937+0.0619358j, 47j],
    [0.0611354+0.0939718j, -47j],
    [-0.0316995+0.046204j, 49j],
    [-0.0809213-0.1179479j, -49j],
    [-0.0710455+0.0982921j, 51j],
    [-0.0826959-0.1144106j, -51j],
    [0.0103866-0.0136514j, 53j],
    [0.0502925+0.0661006j, -53j],
    [-0.0713506+0.0891498j, 55j],
    [0.0111416+0.013921j, -55j],
    [0.0650222-0.0772762j, 57j],
    [0.0138075+0.0164097j, -57j],
    [-0.0069018+0.0078054j, 59j],
    [0.0398966+0.0451196j, -59j],
    [0.0364257-0.0392116j, 61j],
    [-0.0674373-0.072595j, -61j],
    [-0.0073257+0.0075077j, 63j],
    [-0.0589874-0.0604532j, -63j],
    [0.055405-0.0540616j, 65j],
    [0.0069486+0.0067801j, -65j],
    [0.0562264-0.0522317j, 67j],
    [-0.0295823-0.0274805j, -67j],
    [-0.0293132+0.0259198j, 69j],
    [0.0041502+0.0036697j, -69j],
    [-0.0063259+0.0053228j, 71j],
    [-0.0423868-0.0356654j, -71j],
    [-0.0104779+0.008386j, 73j],
    [0.0396812+0.0317587j, -73j],
    [-0.024062+0.0183075j, 75j],
    [-0.009117-0.0069366j, -75j],
    [0.0285046-0.0206031j, 77j],
    [0.0388937+0.0281124j, -77j],
    [0.0262791-0.0180295j, 79j],
    [0.0216302+0.01484j, -79j],
    [-0.025209+0.0164002j, 81j],
    [0.0041274+0.0026851j, -81j],
    [-0.0199894+0.0123171j, 83j],
    [0.0041934+0.0025839j, -83j],
    [0.0043055-0.0025093j, 85j],
    [0.0049595+0.0028905j, -85j],
    [-0.0085183+0.0046884j, 87j],
    [-0.0011185-0.0006156j, -87j],
    [0.0037805-0.0019615j, 89j],
    [0.0096862+0.0050256j, -89j],
    [-0.0089379+0.0043623j, 91j],
    [-0.0011743-0.0005731j, -91j],
    [0.0137951-0.0063186j, 93j],
    [0.0189009+0.0086572j, -93j],
    [0.0157361-0.0067455j, 95j],
    [0.0165131+0.0070786j, -95j],
    [-0.0236771+0.0094687j, 97j],
    [6.677e-04+2.67e-04j, -97j],
    [-0.0255885+0.0095115j, 99j],
    [0.0049513+0.0018405j, -99j],
    [0.0089976-0.0030954j, 101j],
    [0.0056166+0.0019322j, -101j],
    [-0.010482+0.0033207j, 103j],
    [0.0070431+0.0022312j, -103j],
    [0.0097196-0.0028186j, 105j],
    [0.0039195+0.0011366j, -105j],
    [-0.0070956+0.0018702j, 107j],
    [0.0033138+0.0008734j, -107j],
    [0.0199867-0.0047465j, 109j],
    [0.0118939+0.0028246j, -109j],
    [0.024984-0.0052892j, 111j],
    [0.0109786+0.0023242j, -111j],
    [-0.0295266+0.0054974j, 113j],
    [0.0162375+0.0030232j, -113j],
    [-0.0303921+0.0048901j, 115j],
    [0.0316735+0.0050963j, -115j],
    [0.0206482-0.0028044j, 117j],
    [-0.0057649-0.000783j, -117j],
    [0.0062266-0.0006905j, 119j],
    [0.0305862+0.0033919j, -119j],
    [0.0053584-0.0004614j, 121j],
    [-0.0292273-0.0025169j, -121j],
    [0.0184724-0.0011349j, 123j],
    [0.0029226+0.0001796j, -123j],
    [-0.0322556+0.001188j, 125j],
    [-0.0172043-0.0006337j, -125j],
    [-0.0290351+0.0003563j, 127j],
    [3.6234e-03+4.45e-05j, -127j],
    [3.512e-03+4.31e-05j, 129j],
    [-0.0281418+0.0003454j, -129j],
    [-0.0156645-0.000577j, 131j],
    [-0.0293688+0.0010817j, -131j],
    [0.0024997+0.0001536j, 133j],
    [0.0157992-0.0009706j, -133j],
    [-0.0234801-0.002022j, 135j],
    [0.0043048-0.0003707j, -135j],
    [0.0230775+0.0025592j, 137j],
    [0.004698-0.000521j, -137j],
    [-0.0040846-0.0005548j, 139j],
    [0.0146297-0.001987j, -139j],
    [0.0210702+0.0033902j, 141j],
    [-0.0202178+0.0032531j, -141j],
    [0.0101396+0.0018879j, 143j],
    [-0.018438+0.0034329j, -143j],
    [0.0064339+0.0013621j, 145j],
    [0.0146417-0.0030997j, -145j],
    [0.0065398+0.0015531j, 147j],
    [0.0109896-0.0026099j, -147j],
    [0.001709+0.0004504j, 149j],
    [-0.0036594+0.0009645j, -149j]
)

def new_random():
    n = random.randint(2, 20)
    ab = []
    for i in range(n):
        a = (random.uniform(-1, 1) + random.uniform(-1, 1)*1j) / n
        a *= CENTER_CIRCLE_RADIUS
        if (i + 1) % 2 == 1:
            b = math.ceil((i + 1) / 2)
        else:
            b = (i + 1) // -2
        b = b * 1j
        ab.append([a, b])
    print("\n")
    pprint(ab)
    line_surface.fill(BACKGROUND_COLOR)
    return ab

for k in ab:
    k[0] *= CENTER_CIRCLE_RADIUS
c = [0 for i in range(len(ab)+1)]
c_complex = c.copy()
c[0] = SCREEN_CENTER
c_complex[0] = SCREEN_CENTER_COMPLEX
last_point = None
image_number = 1

while running:
    dt = clock.tick(FPS) / 1000  # seconds

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_p or event.key == pg.K_SPACE:
                paused = not paused
            elif event.key == pg.K_c:
                circles_visible = not circles_visible
            elif event.key == pg.K_r:
                ab = new_random()
                # FIXME: duplicated code:
                c = [0 for i in range(len(ab)+1)]
                c_complex = c.copy()
                c[0] = SCREEN_CENTER
                c_complex[0] = SCREEN_CENTER_COMPLEX
                last_point = None
            elif event.key == pg.K_UP:
                speed *= 2
            elif event.key == pg.K_DOWN:
                speed = max(speed / 2, MIN_SPEED)
            elif event.key == pg.K_BACKSPACE:
                line_surface.fill(BACKGROUND_COLOR)

    if not paused:
        circle_surface.fill(BACKGROUND_COLOR_TRANSP)

        t += speed * dt
        if t > math.pi * 2:
            t -= math.pi * 2
            # Prevent t from becoming too big.
            # This only works if the shape has a frequency of 1/(2pi).
            # That means the shape must be finished after one revolution of
            # the innermost circle. This is alway the case if the circle
            # speed follor the pattern 1, -1, 2, -2, 3, -3, ...
            if SAVE_IMAGES:
                running = False

        for i, k in enumerate(ab):
            p = k[0] * math.e ** (k[1] * t) + c_complex[i]
            c_complex[i+1] = p
            c[i+1] = (p.real, p.imag)
            pg.draw.circle(
                circle_surface,
                CIRCLE_COLOR,
                [int(f) for f in c[i]],
                max(int(abs(k[0])), 1),
                1
            )
            pg.draw.line(
                circle_surface,
                CIRCLE_LINE_COLOR,
                c[i],
                c[i+1]
            )

        if last_point is not None:
            if DISCO_MODE:
                for i in range(len(LINE_COLOR)):
                    LINE_COLOR[i] = max(
                        min(
                            LINE_COLOR[i] + random.choice((-20, 0, 20)),
                            255
                        ),
                        0
                    )
            pg.draw.line(
                line_surface,
                LINE_COLOR,
                last_point,
                c[-1],
                2
            )
        last_point = c[-1]

    main_surface.blit(line_surface, (0, 0))
    if circles_visible:
        main_surface.blit(circle_surface, (0, 0))
    pg.display.update()

    pressed = pg.key.get_pressed()
    if pressed[pg.K_s] or SAVE_IMAGES:
        pg.image.save(
            main_surface,
            "screenshots/" + str(image_number).zfill(5) + ".png"
        )
        image_number += 1
        # How to make an animated gif with gimp because I don't
        # understand how to make small gifs with imagemagick:
        # 1. load all images in gimp with file > open as layers
        # 2. image > mode > indexed: 255 colors
        # 3. filters > animation > optimize for gif
        # 4. file > export as: "filename.gif", delay = 1000/fps,
        #    no gif comment, use delay for all frames
        # Experiment with maybe removing the first frames for a better loop.
        #
        # Alternatively there is this way with imagemagick:
        # cd screenshots
        # convert -delay 4 -loop 0 -layers optimize *.png animation.gif
        # The "4" after "-delay" is 100/fps.
        # But the filesize is still larger than with gimp and I don't know why.
        #
        # Either way the file size can be further reduced by converting the
        # animated gif to a mp4 or webm using ffmpeg.
        # Example taken from https://unix.stackexchange.com/a/294892
        # ffmpeg -i animated.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" video.mp4
