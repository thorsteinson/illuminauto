import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage.data import load
from skimage.transform import resize
from skimage.color import rgb2gray
from colorsys import rgb_to_hsl

import time # For performance measurment

TEST_IMAGE_PATH = "/users/caleb/src/illuminati/test_desktop.png"
IMAGE_DIMENSION = 64

lizard = load(TEST_IMAGE_PATH)

# Takes an image as a numpy array, and returns the color of the primary cluster
def color_extract(img):
    # Resize the image
    mini_img = resize(img, (IMAGE_DIMENSION, IMAGE_DIMENSION))

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
    colors = [rgb_vec_to_hsl(c) for c in colors]

    # Get the luminance
    gray = rgb2gray(mini_img)
    luminance = np.average(gray)

    # Return the hue and luminance
    print("Colors: ")
    print(model.cluster_centers_)
    print(colors)
    print("Luminance")
    print(luminance)

# Converts RGB vector into an HSL tuple (scaled to 255)
def rgb_vec_to_hsl(v):
    r = v[0]
    g = v[1]
    b = v[2]
    t = rgb_to_hsl(r, g, b)
    return (t[0] * 255, t[1] * 255, t[2] * 255)

start = time.perf_counter()
color_extract(lizard)
end = time.perf_counter()

print("Total time: %s", end - start)