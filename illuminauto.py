from lightcalc import LightCalc
import numpy as np
import posixpath
import requests
import json
from PIL import ImageGrab
import time # For performance measurment
import os
from os.path import join # For file access
from urllib.parse import urljoin

PERIOD = 2 # Seconds between runs
PHILLIPS_HUE_MAX_BRIGHTNESS = 254
PHILLIPS_HUE_MAX_HUE = 65535
PHILLIPS_HUE_MAX_SAT = 254
PHILLIPS_HUE_TRANSITION_TIME = 10
PHILLIPS_HUE_BRIDGE_IP = "10.0.0.217"
PHILLIPS_HUE_USERNAME = "k-w0WCT6dJUfVudh506zzB-ejM2MPDoj0bntOPeB"
PHILLIPS_HUE_PRIMARY_LIGHT_GROUP_ID = "2"
PHILLIPS_HUE_SECONDARY_LIGHT_GROUP_ID = "3"

# Takes a screenshot of the current screen
# (Not sure how multiple desktops work...)
def take_screenshot(): return np.array(ImageGrab.grab())

def run_forever(freq):
    while True:
        start = time.perf_counter()
        try:
            calc = LightCalc(take_screenshot())
            print(calc)
            change_lights(calc.colors, calc.brightness)
        except OSError as err:
            print("Couldn't caputure the screen, continuing...")
        end = time.perf_counter()

        # Sleep until the end of the next period
        total_time = end-start
        time.sleep(max(0, freq - total_time))

# Takes a color and brightness then returns a map that will act the request body to phillips hue
def construct_hue_body(color, brightness):
    return {
        "on": True,
        "transitiontime": PHILLIPS_HUE_TRANSITION_TIME,
        "hue": int(color["hue"] * PHILLIPS_HUE_MAX_HUE),
        "bri": int(brightness * PHILLIPS_HUE_MAX_BRIGHTNESS),
        "sat": int(color["sat"] * PHILLIPS_HUE_MAX_SAT)
    }

# Constructs the address for a hue group
def construct_hue_url(bridge_ip, username, group_id):
    return urljoin("http://" + bridge_ip,
                   posixpath.join("api", username, "groups", group_id, "action"))

def request_hue(color, brightness, group_id):
    body = construct_hue_body(color, brightness)
    payload = json.dumps(body)
    url = construct_hue_url(PHILLIPS_HUE_BRIDGE_IP, PHILLIPS_HUE_USERNAME, group_id)
    r = requests.put(url, data=payload)

# Makes a request to the phillips hue system
def change_lights(colors, brightness):
    # Get the colors
    primary_color = colors[0]
    if len(colors) < 2:
        # Make the primary and secondary colors the same
        secondary_color = primary_color
    else:
        secondary_color = colors[1]
    
    request_hue(primary_color, brightness, PHILLIPS_HUE_PRIMARY_LIGHT_GROUP_ID)
    request_hue(secondary_color, brightness, PHILLIPS_HUE_SECONDARY_LIGHT_GROUP_ID)

run_forever(PERIOD)