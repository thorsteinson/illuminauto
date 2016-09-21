import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage.data import load
from skimage.measure import block_reduce
from skimage.color import rgb2gray
from colorsys import rgb_to_hls

DEFAULT_BLOCK_SIZE = 32

class LightCalc:
    """A class that takes an image and extracts the main colors out of it"""

    def __init__(self, img, **keywords):
        if type(img) is not np.ndarray:
            raise TypeError('Image provided is not a numpy array. Found ' + type(img))

        img_dimension_size = len(img.shape)
        if img_dimension_size != 3:
            raise TypeError('Image dimension expected to be 3, found: ' + img_dimension_size)

        img_pixel_size = img.shape[2]
        if img_pixel_size != 3:
            raise TypeError('Dimension for pixels expected to be 3, found: ' + img_pixel_size)

        blocksize = keywords.get('blocksize') if 'blocksize' in keywords else DEFAULT_BLOCK_SIZE

        mini_img = reduce_image(img, blocksize)

        self.colors = calc_colors(mini_img)
        self.brightness = calc_brightness(mini_img)

# Takes an image as a numpy array, and returns the color of the primary cluster
# Resize the image
def reduce_image(img, blocksize):
    mini_img = block_reduce(img, block_size=(blocksize, blocksize, 1), func=np.mean)
    # Normalize
    return mini_img / 255

# Performs clustering on an image and returns an array of the different centriods found
def calc_colors(img):
    ## Reshapes the array so that it's a single array of pixels
    img_points = img.reshape(img.shape[0] * img.shape[1], 3)
    bandwidth = estimate_bandwidth(img_points, quantile=0.2, n_samples=500)
    model = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    model.fit(img_points)

    colors = model.cluster_centers_.tolist()

    colors = [rgb_vec_to_hls(c) for c in colors]
    for c in colors:
        amplify(c)
    return colors

# Returns the overall luminance of an image
def calc_brightness(img):
    gray = rgb2gray(img)
    return np.average(gray)

# Converts RGB vector into easier to manipulate HLS color map
def rgb_vec_to_hls(v):
    r = v[0]
    g = v[1]
    b = v[2]
    t = rgb_to_hls(r, g, b)
    return {'hue': t[0],
            'lightness': t[1],
            'sat': t[2]}

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