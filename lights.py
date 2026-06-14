from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import neopixel
import board
import threading
import time
import random
import signal

# ========================
# OSC RECEIVER (Beat)
# ========================
OSC_RECV_IP = "127.0.0.1"
OSC_RECV_PORT = 6540
OSC_BEAT_ADDRESS = "/beat"

beat_event = threading.Event()

def beat_handler(address, *args):
    beat_event.set()

dispatcher = Dispatcher()
dispatcher.map(OSC_BEAT_ADDRESS, beat_handler)

server = ThreadingOSCUDPServer((OSC_RECV_IP, OSC_RECV_PORT), dispatcher)
threading.Thread(target=server.serve_forever, daemon=True).start()

# ========================
# LED CONFIG
# ========================
NUM_PIXELS = 60

pixels = neopixel.NeoPixel(
    board.D2,
    NUM_PIXELS,
    brightness=1.0,
    auto_write=False,
    pixel_order=neopixel.GRB
)

WHITE = (255, 255, 255)
OFF = (0, 0, 0)

led_running = True

def led_loop():
    flash_interval = 2.0
    last_flash_time = time.monotonic()
    current_color = (191, 0, 0)
    red_on = True

    pulse_active = False
    pulse_end_time = 0

    while led_running:
        now = time.monotonic()

        # -------- Normal Flash Timing --------
        if now - last_flash_time >= flash_interval:
            red_on = not red_on
            last_flash_time += flash_interval

            if red_on:
                current_color = (
                    random.randint(0, 255),  # Red
                    random.randint(0, 255),  # Green
                    random.randint(0, 255),  # Blue
                )

        # -------- Beat Trigger --------
        if beat_event.is_set():
            beat_event.clear()
            pulse_active = True
            pulse_end_time = now + 0.1
            pixels.fill(WHITE)
            pixels.show()

        # -------- Handle Pulse --------
        if pulse_active:
            if now >= pulse_end_time:
                pulse_active = False
                pixels.fill(current_color if red_on else OFF)
                pixels.show()
            else:
                time.sleep(0.005)
                continue

        # -------- Maintain Current Color --------
        if not pulse_active:
            pixels.fill(current_color if red_on else OFF)
            pixels.show()

        time.sleep(0.01)

threading.Thread(target=led_loop, daemon=True).start()

def lights_cleanup(sig=None, frame=None):
    pixels.fill(OFF)
    pixels.show()
    server.shutdown()

signal.signal(signal.SIGINT, lights_cleanup)