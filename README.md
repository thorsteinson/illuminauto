# What is this?
This is a simple little python script that caputures the main colors on your
screen and sends those to a Phillips Hue bridge in real time. Basically your
lights will roughly reflect the same contents of what your looking at, adding
a cool level of ambience and immersion. 

## Installation

1. Clone this repository
2. Install the [Anaconda Python](https://www.continuum.io/downloads) distribution
    - This comes with a bunch of scientific computing libraries that make this far
      far easier to work out of the box. You could instead try manually Numpy and Scikit,
      but it's no easy task
3. Install the requests library: `pip install requests`

## Usage

*Warning*, I've only tested running this on Windows, so I'm not sure whether it works
on other platforms. It should be cross platform, but the only bit that may not function
correctly is the screen capture. If that doesn't work, find a way to capture screen input
and turn that into a numpy array and everything else should work.

### Replace Phillips Constants

I don't currently have support for automatically detecting the lights, so you'll have
to manually configure your own light system.

Edit `phillips/core.py`, and change the Constants

- `BRIDGE_IP`: The address of your Phillips Hue Bridge
- `USERNAME`: The username for your Phiilips Hue Application. To create one, take a look
              at [guide on their site](http://www.developers.meethue.com/documentation/getting-started)
              (requires making an account)
- `PRIMARY_LIGHT_GROUP`: This is an array of the lights that will respond to the _primary color_. You want these
                         to be lights that stand out more.
- `SECONDARY_LIGHT_GROUP`: Like the above, but for the _secondary color_. You want these to be
                           a bit more subtle.

Maybe I'll add support for automatically doing the light discovery process, but don't count on it.
Once you've done this once, it will work for good.
### Run the thing

To actually run the app, just execute the following in your favorite terminal

```
python ./illuminauto.py
```

If everything is working properly, then it will start printing out `LightCalc` classes, which means
that it's capturing the desktop colors properly.

### Multiple Monitors
If you have more than one monitor, you can't capture the output of both, but you _can_
choose which monitor you want to watch.

For Windows, open up the display control settings, and then check _make this my main display_.

![Windows 10 Help](/multi_monitor.png)