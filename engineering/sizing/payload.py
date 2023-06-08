import sys
import os

path = os.path.split(sys.argv[0])[0]
sys.path.append(path)

from sizing.rocket import Rocket

class Payload():
    def __init__(self):
        self.mass = 12
        self.length = None
        self.diameter = None
        self.power_draw = None
