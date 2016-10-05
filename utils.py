import math


def calcdist(o1, o2):
    return math.sqrt(float(pow(o1.x - o2.x, 2)) + float(pow(o1.y - o2.y, 2)))


def getglobals():
    """Get global parameters, returned within a dict."""
    params = {
        'ShipRange': 50.,
    }
    return params
