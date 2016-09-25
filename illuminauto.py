from lightcalc.core import LightCalc
from phillips.core import Phillips
import numpy as np
from PIL import ImageGrab
import time # For performance measurment

PERIOD = 0.8 # Seconds between runs
TRANSITION_TIME = 3 # Time for the light to change

# Takes a screenshot of the current screen
# (Not sure how multiple desktops work...)
def take_screenshot(): return np.array(ImageGrab.grab())

def run_forever(freq):
    # Grab the lights
    phillips = Phillips()
    primary_light = phillips.get_primary()
    primary_light.turn_on()
    secondary_light = phillips.get_secondary()
    secondary_light.turn_on()

    while True:
        start = time.perf_counter()
        try:
            calc = LightCalc(take_screenshot())
            print(calc)
            colors = get_colors(calc.colors)

            # Actually changes the lights
            primary_light.change_color(colors[0], calc.brightness, TRANSITION_TIME)
            secondary_light.change_color(colors[1], calc.brightness, TRANSITION_TIME)
        except OSError as err:
            print("Couldn't caputure the screen, continuing...")
        end = time.perf_counter()

        # Sleep until the end of the next period
        total_time = end-start
        time.sleep(max(0, freq - total_time))

# Returns a tuple representing the primary and secondary colors
def get_colors(colors):
    # Get the colors
    primary_color = colors[0]
    if len(colors) < 2:
        # Make the primary and secondary colors the same
        secondary_color = primary_color
    else:
        secondary_color = colors[1]
    
    return (primary_color, secondary_color)

if __name__ == "__main__":
    run_forever(PERIOD)