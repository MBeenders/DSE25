import numpy as np


class Rocket:
    def __init__(self):
        self.mass: float = 0
        self.length: float = 0
        self.diameter: float = 0
        self.power_in: float = 0
        self.power_out: float = 0

        self.engine = self.Engine()
        self.structure = self.Structure()
        
    class Engine:
        def __init__(self):
            self.mass: float = 0
            self.length: float = 0
            self.diameter: float = 0
            self.power_in: float = 0
            self.power_out: float = 0

    class Structure:
        def __init__(self):
            self.mass: float = 0
            self.length: float = 0
            self.diameter: float = 0
            self.power_in: float = 0
            self.power_out: float = 0
