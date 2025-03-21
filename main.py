# noinspection PyUnresolvedReferences
from stellar import StellarUnicorn
# noinspection PyUnresolvedReferences
from picographics import PicoGraphics, DISPLAY_STELLAR_UNICORN
import time

# create a PicoGraphics framebuffer to draw into
graphics = PicoGraphics(display=DISPLAY_STELLAR_UNICORN)

# create our StellarUnicorn object
su = StellarUnicorn()

# start position for scrolling (off the side of the display)
scroll = float(-StellarUnicorn.WIDTH)

# message to scroll
MESSAGE = "Hello World"

# pen colours to draw with
BLACK = graphics.create_pen(0, 0, 0)
YELLOW = graphics.create_pen(128, 128, 0)

while True:
    # determine the scroll position of the text
    width = graphics.measure_text(MESSAGE, 1)
    scroll += 0.25
    if scroll > width:
      scroll = float(-StellarUnicorn.WIDTH)

    # clear the graphics object
    graphics.set_pen(BLACK)
    graphics.clear()

    # draw the text
    graphics.set_pen(YELLOW)
    graphics.text(MESSAGE, round(0 - scroll), 2, -1, 0.55)

    # update the display
    su.update(graphics)

    time.sleep(0.02)