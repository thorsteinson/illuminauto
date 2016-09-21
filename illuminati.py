import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage.data import load
from skimage.measure import block_reduce
from skimage.color import rgb2gray
from colorsys import rgb_to_hls
from urllib.parse import urljoin
import posixpath
import requests
import json

from PIL import ImageGrab

import time # For performance measurment
import os
from os.path import join # For file access

BLOCK_SIZE = 32
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

# Takes an image as a numpy array, and returns the color of the primary cluster
def color_extract(img):
    # Resize the image
    mini_img = block_reduce(img, block_size=(BLOCK_SIZE, BLOCK_SIZE, 1), func=np.mean)
    # Normalize
    mini_img = mini_img / 255

    # Perform clustering
    ## Reshapes the array so that it's a single array of pixels
    img_points = mini_img.reshape(mini_img.shape[0] * mini_img.shape[1], 3)
    bandwidth = estimate_bandwidth(img_points, quantile=0.2, n_samples=500)
    model = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    model.fit(img_points)

    clusters = model.cluster_centers_
    # Grab the first two colors
    colors = clusters[:2].tolist()

    ## Note, we should do a check on the L param to see whether the color is close or not to white / black.
    ## We can set a cutoff point of 20% either way, and that will make the primary for lights either "bright" or "dim"
    colors = [rgb_vec_to_hls(c) for c in colors]
    for c in colors:
        amplify(c)
        
    # Get the luminance
    gray = rgb2gray(mini_img)
    luminance = np.average(gray)

    # Return the hue and luminance
    return {
        'colors': colors,
        'brightness': luminance
    }

# Converts RGB vector into easier to manipulate HLS color map
def rgb_vec_to_hls(v):
    r = v[0]
    g = v[1]
    b = v[2]
    t = rgb_to_hls(r, g, b)
    return {'hue': t[0],
            'lightness': t[1],
            'sat': t[2]}

def run_forever(freq):
    while True:
        start = time.perf_counter()
        try:
            light_calc = color_extract(take_screenshot())
            print(light_calc)
            change_lights(light_calc)
        except OSError as err:
            print("Couldn't caputure the screen, continuing...")
        end = time.perf_counter()

        # Sleep until the end of the next period
        total_time = end-start
        time.sleep(max(0, freq - total_time))

# Amplifies a color so that it's saturation is amplified or cut off (becomes white)
# Takes a color represented as a map
def amplify(color):
    lightness = color['lightness']
    if lightness > 0.85:
        # Just make the light totally white
        color['sat'] = 0
    else:
        # Amplify the saturation to make it pop
        color['sat'] = min(1, color['sat'] + 0.2)

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
def change_lights(light_calc):
    # Get the colors
    colors = light_calc['colors']
    primary_color = colors[0]
    if len(colors) < 2:
        # Make the primary and secondary colors the same
        secondary_color = primary_color
    else:
        secondary_color = colors[1]
    
    request_hue(primary_color, light_calc['brightness'], PHILLIPS_HUE_PRIMARY_LIGHT_GROUP_ID)
    request_hue(secondary_color, light_calc['brightness'], PHILLIPS_HUE_SECONDARY_LIGHT_GROUP_ID)

run_forever(PERIOD)