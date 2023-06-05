import numpy as np


class Subsystem:
    def __init__(self, name: str):
        self.name: str = name
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


class Rocket:
    def __init__(self):
        # Global parameters
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

        # Subsystems
        self.engine_1 = self.Engine("First stage Engine")
        self.engine_2 = self.Engine("Second stage Engine")
        self.recovery_1 = self.Recovery("First stage parachutes")
        self.recovery_2 = self.Recovery("Second stage parachutes")
        self.structure = self.Structure()
        self.electronics = self.Electronics()
        self.payload = self.Payload()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
        
    class Engine(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the subsystem
            """
            Subsystem.__init__(self, name)  # General parameters

            self.isp: float = 0

    class Recovery(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the subsystem
            """
            Subsystem.__init__(self, name)  # General parameters

            # Subsystems
            self.drogue = self.Drogue(name)
            self.main_parachute = self.MainParachute(name)

        class Drogue(Subsystem):
            def __init__(self, name: str):
                """
                :param name: Name of the recovery subsystem
                """
                Subsystem.__init__(self, f"{name} Drogue")  # General parameters

                # Specific parameters
                self.area: float = 0  # [m^2]

        class MainParachute(Subsystem):
            def __init__(self, name: str):
                """
                :param name: Name of the recovery subsystem
                """
                Subsystem.__init__(self, f"{name} Drogue")  # General parameters

                # Specific parameters
                self.area: float = 0  # [m^2]

    class Structure(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Structure")  # General parameters

    class Electronics(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Electronics")  # General parameters

    class Payload(Subsystem):
        def __init__(self):
            Subsystem.__init__(self, "Payload")  # General parameters


if __name__ == "__main__":
    test_rocket = Rocket()
    print(test_rocket.engine_1.name)
