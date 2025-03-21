# noinspection PyUnresolvedReferences
from stellar import StellarUnicorn
# noinspection PyUnresolvedReferences
from picographics import PicoGraphics, DISPLAY_STELLAR_UNICORN
import WIFI_CONFIG
from network_manager import NetworkManager
import asyncio
import tinyweb.server
import time

host = "192.168.178.16"
port = 80

app = tinyweb.server.webserver()


@app.route('/')
async def index(request, response):
    await response.send_file('index.html', content_type='text/html')


# create a PicoGraphics framebuffer to draw into
graphics = PicoGraphics(display=DISPLAY_STELLAR_UNICORN)

# create our StellarUnicorn object
su = StellarUnicorn()
su.set_brightness(0.5)

# start position for scrolling (off the side of the display)
SCROLL = float(-StellarUnicorn.WIDTH)

# pen colours to draw with
BLACK = (0, 0, 0)
YELLOW = (128, 128, 0)
WHITE = (255, 255, 255)

# message to scroll
MESSAGE = "BOOT"
FOREGROUND_COLOUR = YELLOW
BACKGROUND_COLOUR = BLACK


def convert_colour(colour_string):
    global graphics
    colours = colour_string.split(',')
    print(colours)
    return int(colours[0]), int(colours[1]), int(colours[2])


class TextController:

    def get(self, data):
        global MESSAGE, FOREGROUND_COLOUR, BACKGROUND_COLOUR
        print(data)
        if 'text' in data.keys():
            MESSAGE = data['text']
        if 'colourfg' in data.keys():
            FOREGROUND_COLOUR = convert_colour(data['colourfg'])
            print('FOREGROUND_COLOUR convert {} -> {}'.format(data['colourfg'], convert_colour(data['colourfg'])))
        if 'colourbg' in data.keys():
            BACKGROUND_COLOUR = convert_colour(data['colourbg'])
            print('BACKGROUND_COLOUR convert {} -> {}'.format(data['colourbg'], convert_colour(data['colourbg'])))
        return {'message': 'text updated'}, 201

    def post(self, data):
        return {'message': 'text updated'}, 201


async def animate_text():
    global SCROLL, MESSAGE, FOREGROUND_COLOUR, BACKGROUND_COLOUR
    while True:
        # check brightness hardware buttons
        if su.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_UP):
            su.adjust_brightness(+0.01)
        if su.is_pressed(StellarUnicorn.SWITCH_BRIGHTNESS_DOWN):
            su.adjust_brightness(-0.01)

        # determine the scroll position of the text
        width = graphics.measure_text(MESSAGE, 1)
        SCROLL += 0.25
        if SCROLL > width:
            SCROLL = float(-StellarUnicorn.WIDTH)

        # clear the graphics object
        set_pen(BACKGROUND_COLOUR)
        graphics.clear()

        # draw the text
        set_pen(FOREGROUND_COLOUR)
        graphics.text(MESSAGE, round(0 - SCROLL), 2, -1, 0.55)

        # update the display
        su.update(graphics)

        await asyncio.sleep(0.02)

def set_pen(rgb_tuple):
    return graphics.set_pen(graphics.create_pen(int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2])));

def show_boot_screen():
    set_pen(BLACK)
    graphics.clear()

    set_pen(WHITE)
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
    show_boot_screen()

    app.add_resource(TextController, '/update')

    # Wi-Fi setup
    network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
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
