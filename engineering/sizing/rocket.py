import numpy as np


class Stage:
    def __init__(self, name: str):
        self.id: str = "0.0"
        self.name: str = name
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

        # Initialize possible components
        self.engine: Subsystem | None = None
        self.recovery: Subsystem | None = None
        self.structure: Subsystem | None = None
        self.electronics: Subsystem | None = None
        self.payload: Subsystem | None = None

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


class Subsystem:
    def __init__(self, name: str):
        self.id: str = "0.0"
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


class Rocket:
    def __init__(self):
        # Global parameters
        self.id: str = "0"
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

        # Stage
        self.stage_1: Stage = self.Stage1("First Stage")
        self.stage_2: Stage = self.Stage2("Second Stage")

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    class Stage1(Stage):
        def __init__(self, name: str):
            """
            :param name: Name of the stage
            """
            super().__init__(name)  # General parameters

            # Specific
            self.engine: Subsystem = Engine("First stage Engine")
            self.recovery: Subsystem = Recovery("First stage parachutes")
            self.structure: Subsystem = Structure()
            self.electronics: Subsystem = Electronics()
            self.payload: Subsystem = Payload()

    class Stage2(Stage):
        def __init__(self, name: str):
            """
            :param name: Name of the stage
            """
            super().__init__(name)  # General parameters

            # Specific
            self.engine: Subsystem = Engine("First stage Engine")
            self.recovery: Subsystem = Recovery("First stage parachutes")
            self.structure: Subsystem = Structure()


if __name__ == "__main__":
    test_rocket: Rocket = Rocket()
    print(test_rocket.stage_1.engine.mass)
    print(test_rocket.stage_2.engine.isp)
