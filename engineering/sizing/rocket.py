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

        self.dry_mass: float = 0 # [kg]

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
        self.oxidizer: dict = {}
        self.fuel: dict = {}

        self.mass_flow_rate: np.ndarray = np.ones((2, 1000), dtype=float) # Mass flow rate profile engine
        self.mass_fuel_start: float = 100 # Fuel mass at start of burn [kg]
        self.rho_fuel: float = 1800 # Density of the fuel [kg/m^3]
        self.height_fuel: float = 0.5 # Length of the fuel grain (all stacked) [m]
        self.inner_diameter: float = 0.18 # Inner diameter of motor, so diameter of fuel grain [m]
        self.MMOI_casing: float = 1 # Mass moment of inertia of dry engine (everything excluding fuel) [kg*m^2]

    def calculate_moi(self, time: float):
        mass_lost = sum(self.mass_flow_rate[1][:time])  # Burnt fuel up to now
        mass_fuel = self.mass_fuel_start - mass_lost  # Fuel mass left
        Section_area = mass_fuel/ (self.rho_fuel * self.height_fuel)  # Area of a grain section at the moment, assuming perfect radial burning
        r2 = self.inner_diameter/2   # Diameter to radius
        r1_sq = r2**2 - (Section_area/np.pi) # Square of the inner radius of the grain section at the moment
        MMOI_fuel = 0.5*mass_fuel*(r1_sq + r2**2) # Mass moment of inertia of the fuel alone
        MMOI_engine = MMOI_fuel + self.MMOI_casing
        return MMOI_engine


class Recovery(Subsystem):
    def __init__(self, name: str):
        """
        :param name: Name of the subsystem
        """
        Subsystem.__init__(self, name)  # General parameters

        # Subsystems
        self.drogue = self.Drogue(name)
        self.main_parachute = self.MainParachute(name)

        self.descent_rate: float = 0 # [m/s]
        self.material_density: float = 0 # [kg/m^3]
        self.material_cost: float = 0 # [euros/m^2]

    class Drogue(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the recovery subsystem
            """
            Subsystem.__init__(self, f"{name} Drogue")  # General parameters

            # Specific parameters
            self.area: float = 0  # [m^2]
            self.c_D: float = 0

    class MainParachute(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the recovery subsystem
            """
            Subsystem.__init__(self, f"{name} Drogue")  # General parameters

            # Specific parameters
            self.area: float = 0  # [m^2]
            self.c_D: float = 0


class Structure(Subsystem):
    def __init__(self):
        Subsystem.__init__(self, "Structure")  # General parameters


class Electronics(Subsystem): #should be 3 objects one for the 1st stage electronics, one for the 2nd stage electronics, and one for the payload (though payload should not have a separate communication system)
    def __init__(self, name: str):
        Subsystem.__init__(self, f"{name}Electronics")
        # General parameters
        self.time: float
        self.power_sensors: float
        self.datarate: int


        self.powersystem = self.Power(name)
        self.communicationsystem = self.Communication(name)
        self.blackbox = self.Blackbox(name)
    
    class Power(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Power")
            self.avg_voltage: float
            self.dod: float
            self.power_density: float
            self.power_volume: float
            self.margin: float

            #final outputs
            self.tot_power: float
            self.mass_bat: float
            self.volume_bat: float
            

            


    
    class Communication(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Communication")
            self.frequency: float
            self.power_com: float
            self.gain_tx: float
            self.diameter_antenna_gs: float
            self.antenna_snr: float
            self.antenna_efficiency_gs: float
            self.margin: float
            self.max_range: int
            self.modulation: str
            self.max_speed: float

            #final outputs
            self.bandwidth: float
            self.SNR: float
            self.capacity: float
            


    
    class Blackbox(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Blackbox")
            
            self.margin: float
            self.storage: float



class Payload(Subsystem):
    def __init__(self, name):
        Subsystem.__init__(self, "Payload")  # General parameters
        self.power_system = self.Power(name)
        self.time: int
        self.power_sensors: float


    class Power(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Power")
            self.avg_voltage: float
            self.dod: float
            self.mass_bat: float
            self.tot_power: float
            self.power_density: float
            self.power_volume: float
            self.margin: float


class Rocket:
    def __init__(self, simulator):
        # Global parameters
        self.id: str = "0"
        self.mass: float = 0  # [kg]
        self.length: float = 0  # [m]
        self.diameter: float = 0  # [m]
        self.power_in: float = 0  # [W]
        self.power_out: float = 0  # [W]

        # Simulator
        self.simulator = simulator

        # Stage
        self.stage1: Stage = self.Stage1("First Stage")
        self.stage2: Stage = self.Stage2("Second Stage")

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

    class Stage2(Stage):
        def __init__(self, name: str):
            """
            :param name: Name of the stage
            """
            super().__init__(name)  # General parameters

            # Specific
            self.engine: Subsystem = Engine("Second stage Engine")
            self.recovery: Subsystem = Recovery("Second stage Parachutes")
            self.structure: Subsystem = Structure()
            self.electronics: Subsystem = Electronics()
            self.payload: Subsystem = Payload()


if __name__ == "__main__":
    test_rocket: Rocket = Rocket()
    print(test_rocket.stage1.engine.mass)
    print(test_rocket.stage2.engine.isp)
