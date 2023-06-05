import numpy as np


class Subsystem:
    def __init__(self, name: str):
        self.name: str = name
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]


class Rocket:
    def __init__(self):
        # Global parameters
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

        # Subsystems
        self.engine = self.Engine()
        self.structure = self.Structure()
        self.recovery = self.Recovery()
        self.electronics = self.Electronics()
        self.payload = self.Payload()
        
    class Engine(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Engine")

    class Structure(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Structure")

    class Recovery(Subsystem):
        def __init__(self):
            # General parameters
            Subsystem.__init__(self, "Recovery")

            # Subsystems
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

    class Electronics(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Electronics")

    class Payload(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Payload")


if __name__ == "__main__":
    test_rocket = Rocket()
    print(test_rocket.engine.name)
