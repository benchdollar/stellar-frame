# noinspection PyUnresolvedReferences
from stellar import StellarUnicorn
# noinspection PyUnresolvedReferences
from picographics import PicoGraphics, DISPLAY_STELLAR_UNICORN
import WIFI_CONFIG
from network_manager import NetworkManager
import uasyncio as asyncio
import uasyncio.core
from tinyweb.server import webserver
import time

host = "192.168.178.16"
port = 80

app = webserver()


@app.route('/')
async def index(request, response):
    await response.send_file('index.html', content_type='text/html')


# create a PicoGraphics framebuffer to draw into
graphics = PicoGraphics(display=DISPLAY_STELLAR_UNICORN)

# create our StellarUnicorn object
su = StellarUnicorn()
su.set_brightness(0.5)

# start position for scrolling (off the side of the display)
scroll = float(-StellarUnicorn.WIDTH)

# message to scroll
MESSAGE = "BOOT"

# pen colours to draw with
BLACK = graphics.create_pen(0, 0, 0)
YELLOW = graphics.create_pen(128, 128, 0)
WHITE = graphics.create_pen(255, 255, 255)


async def animate_text():
    global scroll
    while True:
        # check brightness hardware buttons
        if su.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_UP):
            su.adjust_brightness(+0.01)
        if su.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_DOWN):
            su.adjust_brightness(-0.01)

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

        await asyncio.sleep(0.02)


def show_boot_screen():
    graphics.set_pen(BLACK)
    graphics.clear()

    graphics.set_pen(WHITE)
    graphics.set_font('bitmap6')
    graphics.text(MESSAGE, 0, 0, -1, 0.55)
    su.update(graphics)

    time.sleep(5.0)


def status_handler(mode, status, ip):
    global MESSAGE
    print("Network: {}".format(WIFI_CONFIG.SSID))
    status_text = "Connecting..."
    if status is not None:
        if status:
            status_text = "Connection successful!"
        else:
            status_text = "Connection failed!"

    print(status_text)
    print("IP: {}".format(ip))
    MESSAGE = "{}".format(ip)


def setup():
    # Wi-Fi
    network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)

    # app.add_resource(text, '/update')

    show_boot_screen()

    asyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
    while not network_manager.isconnected():
        time.sleep(0.1)


setup()

# The following is required to run both the web server and the scrolling text coherently
app._server_coro = app._tcp_server(host, port, app.backlog)
loop = asyncio.get_event_loop()
t1 = loop.create_task(animate_text())
t2 = loop.create_task(app._server_coro)
loop.run_forever()
