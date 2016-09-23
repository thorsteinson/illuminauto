import posixpath
import requests
import json
import os
from os.path import join
from urllib.parse import urljoin

# Constants for converting to hue specific colors
MAX_BRIGHTNESS = 254
MAX_HUE = 65535
MAX_SAT = 254

# Temp constants that we will eventually generate dynamically
BRIDGE_IP = "10.0.0.217"
USERNAME = "k-w0WCT6dJUfVudh506zzB-ejM2MPDoj0bntOPeB"
PRIMARY_LIGHT_GROUP = [2, 3]
SECONDARY_LIGHT_GROUP = [1]

class Phillips:
    """A class for accessing light groups, and establishing a connection to the Phillips Hue Bridge"""
    def __init__(self):
        self.bridge_ip = BRIDGE_IP
        self.username = USERNAME

    # Constructs the address for a hue light
    def _construct_hue_url(self, light_id):
        return urljoin("http://" + self.bridge_ip,
                        posixpath.join("api", self.username, "lights", str(light_id), "state"))
    
    def get_secondary(self):
        urls = [self._construct_hue_url(id) for id in SECONDARY_LIGHT_GROUP]
        return LightGroup(urls)
    def get_primary(self):
        urls = [self._construct_hue_url(id) for id in PRIMARY_LIGHT_GROUP]
        return LightGroup(urls)

class LightGroup:
    """A group of phillips lights that can have it's color altered"""
    def __init__(self, light_urls):
        # The urls for each light in the group. We avoid the groups API because it's more performant
        # to directly access the lights themselves unless a group has at least a dozen lights
        self.light_urls = light_urls
    
    # Makes a request to change the color
    def change_color(self, color, brightness, transition_time):
        body = construct_hue_body(color, brightness, transition_time)
        payload = json.dumps(body)
        for url in self.light_urls:
            requests.put(url, data=payload, timeout=0.5)
    
# Takes a color and brightness then returns a map that will act the request body to phillips hue
def construct_hue_body(color, brightness, transition_time):
    return {
        "transitiontime": transition_time,
        "hue": int(color["hue"] * MAX_HUE),
        "bri": int(brightness * MAX_BRIGHTNESS),
        "sat": int(color["sat"] * MAX_SAT)
    }