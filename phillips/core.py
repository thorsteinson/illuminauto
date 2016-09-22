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
PRIMARY_LIGHT_GROUP_ID = "2"
SECONDARY_LIGHT_GROUP_ID = "3"

class Phillips:
    """A class for accessing light groups, and establishing a connection to the Phillips Hue Bridge"""
    def __init__(self):
        self.bridge_ip = BRIDGE_IP
        self.username = USERNAME

    # Constructs the address for a hue group
    def _construct_hue_url(self, group_id):
        return urljoin("http://" + self.bridge_ip,
                        posixpath.join("api", self.username, "groups", group_id, "action"))
    
    def get_secondary(self):
        return LightGroup(self._construct_hue_url(SECONDARY_LIGHT_GROUP_ID))
    def get_primary(self):
        return LightGroup(self._construct_hue_url(PRIMARY_LIGHT_GROUP_ID))

class LightGroup:
    """A group of phillips lights that can have it's color altered"""
    def __init__(self, url):
        self.url = url
    
    # Makes a request to change the color
    def change_color(self, color, brightness, transition_time):
        body = construct_hue_body(color, brightness, transition_time)
        payload = json.dumps(body)
        r = requests.put(self.url, data=payload)
    
# Takes a color and brightness then returns a map that will act the request body to phillips hue
def construct_hue_body(color, brightness, transition_time):
    return {
        "on": True,
        "transitiontime": transition_time,
        "hue": int(color["hue"] *MAX_HUE),
        "bri": int(brightness * MAX_BRIGHTNESS),
        "sat": int(color["sat"] *MAX_SAT)
    }