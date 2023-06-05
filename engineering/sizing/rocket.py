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
        self.recovery = self.Recovery()
        self.electronics = self.Electronics()
        self.payload = self.Payload()
        
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

    class Recovery:
        def __init__(self):
            self.mass: float = 0  # Total mass of recovery system [kg]

            self.drogue = self.Drogue()
            self.main_parachute = self.MainParachute()

        class Drogue:
            def __init__(self):
                self.mass: float = 0  # [kg]
                self.area: float = 0  # [m^2]

        class MainParachute:
            def __init__(self):
                self.mass: float = 0  # [kg]
                self.area: float = 0  # [m^2]

    class Electronics:
        def __init__(self):
            self.mass: float = 0
            self.length: float = 0
            self.diameter: float = 0
            self.power_in: float = 0
            self.power_out: float = 0

    class Payload:
        def __init__(self):
            self.mass: float = 0
            self.length: float = 0
            self.diameter: float = 0
            self.power_in: float = 0
            self.power_out: float = 0
