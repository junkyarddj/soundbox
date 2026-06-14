import lgpio
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import board
import time
import threading
import signal
import sys
import random
import lights

# ========================
# OSC SENDER (Buttons)
# ========================

OSC_SEND_CHANNEL_PATH = "/channel"
OSC_SEND_TEST_PATH = "/test"
OSC_SEND_KILL_PATH = "/kill"
OSC_SEND_GENRE_SWAP_PATH = "/genre_swap"

client = udp_client.SimpleUDPClient(OSC_SEND_IP, OSC_SEND_PORT)

h = lgpio.gpiochip_open(0)

MAGNETIC_BUTTONS = {
    7: "1", 6: "2", 19: "3", 13: "4",
    20: "5", 12: "6", 16: "7", 8: "8",
    9: "9", 11: "10", 10: "11", 22: "12",
    26: "13", 21: "14", 27: "15", 25: "16",
}

BUTTONS = [15, 18, 23, 24]

GENRES = [
    "channels_house.rb",
    "channels_techhouse.rb",
    "channels_slaphouse.rb",
    "channels_hiphop.rb", 
    "channels_punk.rb",
    "channels_pop.rb",
    "channels_dnb.rb",
    "channels_ambient.rb"
]

CURRENT_GENRE_ID = 0
client.send_message(OSC_SEND_GENRE_SWAP_PATH, GENRES[CURRENT_GENRE_ID])


DEBOUNCE_TIME = 0.05  # 50ms (adjust if needed)

last_time = {}
last_state = {}

for mb in MAGNETIC_BUTTONS:
    lgpio.gpio_claim_input(h, mb, lgpio.SET_PULL_UP)
    last_time[mb] = 0
    last_state[mb] = 0  # default HIGH (not pressed)

for b in BUTTONS:
    lgpio.gpio_claim_input(h, b, lgpio.SET_PULL_UP)
    last_time[b] = 0
    last_state[b] = 0  # not pressed

def button_event(chip, gpio, level, timestamp):
    global CURRENT_GENRE_ID

    now = time.monotonic()

    # Debounce time filter
    if now - last_time[gpio] < DEBOUNCE_TIME:
        return

    state = 1 if level == 0 else 0  # pressed = 1

    # Ignore duplicate state
    if state == last_state[gpio]:
        return

    last_time[gpio] = now
    last_state[gpio] = state

    if gpio == 18 and state == 1:
        print("KILL ALL TRIGGERED (18)")
        client.send_message(OSC_SEND_KILL_PATH, 1)
    elif gpio == 23 and state == 1:
        CURRENT_GENRE_ID = (CURRENT_GENRE_ID - 1) % len(GENRES)
        print("GENRE CHANGE TRIGGERED (23):", GENRES[CURRENT_GENRE_ID])
        client.send_message(OSC_SEND_GENRE_SWAP_PATH, GENRES[CURRENT_GENRE_ID])
    elif gpio == 24 and state == 1:
        CURRENT_GENRE_ID = (CURRENT_GENRE_ID + 1) % len(GENRES)
        print("GENRE CHANGE TRIGGERED (24):", GENRES[CURRENT_GENRE_ID])
        client.send_message(OSC_SEND_GENRE_SWAP_PATH, GENRES[CURRENT_GENRE_ID])

    elif gpio in MAGNETIC_BUTTONS:
        print("MAG BUTTON:")
        ch = MAGNETIC_BUTTONS[gpio]
        if last_state.get(15, 0) == 1 and state == 1:
            print("TEST TRIGGERED (15)")
            client.send_message(OSC_SEND_TEST_PATH, int(ch))    
        else:
            print("Channel", ch, " (", gpio, ")", "is", state)
            client.send_message(OSC_SEND_CHANNEL_PATH, [ch, state])

for mb in MAGNETIC_BUTTONS:
    lgpio.gpio_claim_alert(h, mb, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP)
    lgpio.callback(h, mb, lgpio.BOTH_EDGES, button_event)

for b in BUTTONS:
    lgpio.gpio_claim_alert(h, b, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP)
    lgpio.callback(h, b, lgpio.BOTH_EDGES, button_event)

# ========================
# CLEAN EXIT
# ========================
def cleanup(sig=None, frame=None):
    global led_running
    led_running = False
    lgpio.gpiochip_close(h)
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

print("Running...")

while True:
    time.sleep(0.1)