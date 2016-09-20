import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage.data import load
from skimage.measure import block_reduce
from skimage.color import rgb2gray
from colorsys import rgb_to_hls

from PIL import ImageGrab

import time # For performance measurment
import os
from os.path import join # For file access

BLOCK_SIZE = 32
FREQUENCY = 1 # Seconds between runs
PHILLIPS_HUE_MAX_BRIGHTNESS = 254
PHILLIPS_HUE_MAX_HUE = 65535
PHILLIPS_HUE_MAX_SAT = 65535

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

    # Get the luminance
    gray = rgb2gray(mini_img)
    luminance = np.average(gray)

    # Return the hue and luminance
    return {
        'colors': colors,
        'brightness': round(luminance * PHILLIPS_HUE_MAX_BRIGHTNESS)
    }

# Converts RGB vector into colors that are scaled appropriately for the Phillips Hue
def rgb_vec_to_hls(v):
    r = v[0]
    g = v[1]
    b = v[2]
    t = rgb_to_hls(r, g, b)
    return {'hue': round(t[0] * PHILLIPS_HUE_MAX_HUE),
            'brightness': round(t[1] * PHILLIPS_HUE_MAX_BRIGHTNESS),
            'sat': round(t[2] * PHILLIPS_HUE_MAX_SAT)}

def run_forever(freq):
    while True:
        start = time.perf_counter()
        try:
            colors = color_extract(take_screenshot())
            print(colors)
        except OSError as err:
            print("Couldn't caputure the screen, continuing...")
        end = time.perf_counter()

        # Sleep until the end of the next second
        total_time = end-start
        time.sleep(max(0, freq - total_time))

run_forever(FREQUENCY)