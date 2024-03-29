import numpy as np
from colorama import Fore


class Stage:
    def __init__(self, name: str, payload, shoulder, nosecone):
        self.id: str = "0.0"
        self.name: str = name

        # Mass
        self.mass: float | None = None  # [kg]
        self.dry_mass: float | None = None  # [kg]

        # Dimension
        self.length: float | None = None  # [m]
        self.diameter: float | None = None  # [m]
        self.wetted_area: float | None = None  # [m^2]
        self.flow_area: float | None = None  # [m^2]

        # Locations (From the Nose)
        self.max_cg_location: float | None = None  # [m]
        self.min_cg_location: float | None = None  # [m]
        self.cp_location: float | None = None  # [m]

        self.stability_margin: float | None = None  # [-]

        # Cost
        self.cost: float | None = None  # [euros]

        # Initialize possible components
        self.engine: Subsystem | None = None
        self.recovery: Subsystem | None = None
        self.electronics: Subsystem | None = None
        self.fins: Subsystem | None = None

        if payload:
            self.payload: Subsystem | None = None
        if nosecone:
            self.nosecone: Subsystem | None = None
        if shoulder:
            self.shoulder: Subsystem | None = None

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


class Subsystem:
    def __init__(self, name: str):
        self.id: str = "0.0"
        self.name: str = name

        # Mass
        self.mass: float | None = None  # [kg]
        self.dry_mass: float | None = None   # [kg]

        # Dimension
        self.length: float | None = None   # [m]
        self.diameter: float | None = None   # [m]
        self.wetted_area: float | None = None   # [m^2]
        self.flow_area: float | None = None  # [m^2]

        # Locations (From the Nose)
        self.max_cg_location: float | None = None   # [m]
        self.min_cg_location: float | None = None   # [m]
        self.cp_location: float | None = None   # [m]

        # Cost
        self.cost: float | None = None   # [euros]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


class Engine(Subsystem):
    def __init__(self, name: str, tower):
        """
        :param name: Name of the subsystem
        """
        Subsystem.__init__(self, name)  # General parameters

        # General
        self.isp: float | None = None
        self.impulse: float | None = None
        self.burn_time: float | None = None
        self.thrust: float | None = None

        # Structure
        self.bulkhead_mass: float | None = None

        # Chamber
        self.chamber_pressure: float | None = None
        self.chamber_gamma: float | None = None
        self.chamber_temperature: float | None = None
        self.chamber_volume: float | None = None
        self.chamber_length: float | None = None
        self.cc: float | None = None
        self.c_star: float | None = None
        self.area_exit: float | None = None
        self.volumetric_constant: float | None = None

        # Propellant
        self.propellant_mass: float | None = None
        self.propellant_density: float | None = None
        self.molecular_weight: float | None = None
        self.grain_diameter: float | None = None

        # Casing
        self.casing_mass: float | None = None
        self.casing_thickness: float | None = None
        self.casing_density: float | None = None
        self.yield_strength: float | None = None
        self.safety_factor: float | None = None
        self.liner_thickness: float | None = None

        # Nozzle
        self.nozzle_mass: float | None = None
        self.nozzle_thickness: float | None = None
        self.nozzle_density: float | None = None
        self.nozzle_throat_area: float | None = None
        self.nozzle_exit_area: float | None = None
        self.nozzle_area_ratio: float | None = None
        self.nozzle_length: float | None = None

        # Chemicals
        self.oxidizer: dict = {}
        self.fuel: dict = {}

        # Launch Tower
        if tower:
            self.launch_tower_length: float | None = None
            self.launch_exit_velocity: float | None = None

        # Sim stuff
        self.thrust_curve: np.array = np.zeros(10000, dtype=float)  # Engine thrust curve over time
        self.fuel_mass_curve: np.array = np.zeros(10000, dtype=float)  # Total engine mass over time
        self.mmoi: np.array = np.zeros(10000, dtype=float)  # Mass Moment of Inertia over time

        self.mass_flow_rate: np.ndarray = np.ones((2, 1000), dtype=float)  # Mass flow rate profile engine
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
    def __init__(self, name: str, drogue):
        """
        :param name: Name of the subsystem
        """
        Subsystem.__init__(self, name)  # General parameters

        # Subsystems
        if drogue:
            self.drogue = self.Drogue(name)
        self.main_parachute = self.MainParachute(name)

        self.material_density: float | None = None  # [kg/m^2]
        self.material_cost: float | None = None  # [euros/m^2]
        self.line_density: float | None = None  # [kg/m]
        self.line_cost: float | None = None  # [euros/m]
        self.m_gas: float | None = None  # [kg]
        self.gas_cost: float | None = None  # [euros]
        self.n_gas: float | None = None  # [-]

        # Final outputs
        self.gas_total_mass: float | None = 0  # [kg]
        self.gas_total_cost: float | None = 0  # [euros]

    class Drogue(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the recovery subsystem
            """
            Subsystem.__init__(self, f"{name} Drogue")  # General parameters

            # Specific parameters
            self.c_D: float | None = None
            self.rho: float | None = None
            self.descent_rate: float | None = None  # [m/s]
            self.line_l_d: float | None = None  # [-] Suspension line length over nominal diameter ratio
            self.n_line: float | None = None  # [-] Number of suspension lines
            self.packing_density: float | None = None  # [kg/m^3]

            # Final output
            self.area: float | None = 0  # [m^2]

    class MainParachute(Subsystem):
        def __init__(self, name: str):
            """
            :param name: Name of the recovery subsystem
            """
            Subsystem.__init__(self, f"{name} Drogue")  # General parameters

            # Specific parameters
            self.c_D: float | None = None
            self.rho: float | None = None
            self.descent_rate: float | None = None  # [m/s]
            self.line_l_d: float | None = None  # [-] Suspension line length over nominal diameter ratio
            self.n_line: float | None = None  # [-] Number of suspension lines
            self.packing_density: float | None = None  # [kg/m^3]

            # Final output
            self.area: float | None = 0  # [m^2]


class Nosecone(Subsystem):
    def __init__(self, name):
        Subsystem.__init__(self, name)

        self.base_radius: float | None = None
        self.axial_distance: float | None = None
        self.thickness: float | None = None
        self.density: float | None = None
        self.drag_coefficient: float | None = None
        self.joint_angle: float | None = None


class Fins(Subsystem):
    def __init__(self, name):
        Subsystem.__init__(self, name)

        self.amount: float | None = None

        self.chord_root: float | None = None
        self.chord_tip: float | None = None
        self.span: float | None = None
        self.sweep: float | None = None
        self.mac: float | None = None
        self.thickness: float | None = None
        self.density: float | None = None

        self.shear_modulus: float | None = None
        self.flutter_margin: float | None = None


class Shoulder(Subsystem):
    def __init__(self, name):
        Subsystem.__init__(self, name)  # General parameters

        self.thickness: float | None = None
        self.density: float | None = None


class Structure(Subsystem):
    def __init__(self):
        Subsystem.__init__(self, "Structure")  # General parameters


# Should be 3 objects one for the 1st stage electronics, one for the 2nd stage electronics, and one for the payload (though payload should not have a separate communication system)
class Electronics(Subsystem):
    def __init__(self, name: str):
        Subsystem.__init__(self, f"{name}Electronics")
        # General parameters
        self.time: float | None = None
        self.power_sensors: float | None = None
        self.datarate: float | None = None

        self.powersystem = self.Power(name)
        self.communicationsystem = self.Communication(name)
        self.blackbox = self.Blackbox(name)

    class Power(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Power")

            self.avg_voltage: float | None = None
            self.dod: float | None = None
            self.power_density: float = 140  # Wh/kg
            self.power_volume: float = 250000  # Wh/m^3
            self.margin: float | None = None

            # Final outputs
            self.tot_power: float | None = 0
            self.mass_bat: float | None = 0
            self.volume_bat: float | None = 0
            self.bat_size: float | None = 0
    
    class Communication(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Communication")
            self.frequency: float | None = None
            self.power_com: float | None = None
            self.gain_tx: float | None = None
            self.diameter_antenna_gs: float | None = None
            self.antenna_snr: float | None = None
            self.antenna_efficiency_gs: float | None = None
            self.margin: float | None = None
            self.max_range: float | None = None
            self.modulation: float | None = None
            self.max_speed: float | None = None

            # Final outputs
            self.bandwidth: float | None = 0
            self.SNR: float | None = 0
            self.capacity: float | None = 0

    class Blackbox(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Blackbox")

            self.margin: float | None = None

            # Final output
            self.storage: float | None = 0


class Payload(Subsystem):
    def __init__(self, name):
        Subsystem.__init__(self, "Payload")  # General parameters

        self.power_system = self.Power(name)
        self.sensor_mass: int | None = None
        self.time: float | None = None
        self.power_sensors: float | None = None

        self.powersystem = self.Power(name)
        self.blackbox = self.Blackbox(name)

    class Power(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Power")
            self.avg_voltage: float | None = None
            self.dod: float | None = None
            self.power_density: float = 140  # Wh/kg
            self.power_volume: float = 250000  # Wh/m^3
            self.margin: float | None = None

            # Final outputs
            self.tot_power: float | None = 0
            self.mass_bat: float | None = 0
            self.volume_bat: float | None = 0
            self.bat_size: float | None = 0

    class Blackbox(Subsystem):
        def __init__(self, name: str):
            Subsystem.__init__(self, f"{name} Blackbox")
            
            self.margin: float | None = None

            # Final output
            self.storage: float | None = 0


class Rocket:
    def __init__(self, simulator):
        # Global parameters
        self.id: str = "0"

        # Mass
        self.mass: float | None = None  # [kg]
        self.dry_mass: float | None = None  # [kg]

        # Dimension
        self.length: float | None = None  # [m]
        self.diameter: float | None = None  # [m]
        self.wetted_area: float | None = None  # [m^2]
        self.flow_area: float | None = None  # [m^2]

        # Locations (From the Nose)
        self.max_cg_location: float | None = None  # [m]
        self.min_cg_location: float | None = None  # [m]
        self.cp_location: float | None = None  # [m]

        self.stability_margin: float | None = None  # [-]
        self.fineness_ratio: float | None = None  # [-]

        # Cost
        self.cost: float | None = None  # [euros]

        # Specific
        self.cd: float = 0.65

        # Simulator
        self.simulator = simulator

        # Stage
        self.stage1: Stage = self.Stage1("First Stage")
        self.stage2: Stage = self.Stage2("Second Stage")

        # List of attributes in the Subsystem parent class
        # Exclude variables that should not be summed
        self.excluded_variables: list = ["id", "name", "max_cg_location", "min_cg_location", "cp_location",
                                         "diameter", "stability_margin"]

        sample_subsystem: Subsystem = Subsystem("Sample")
        self.compare_list: list = []
        for key, _ in sample_subsystem.__dict__.items():
            if key not in self.excluded_variables:
                self.compare_list.append(key)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    class Stage1(Stage):
        def __init__(self, name: str):
            """
            :param name: Name of the stage
            """
            super().__init__(name, False, True, False)  # General parameters

            # Specific
            self.engine: Subsystem = Engine("First stage Engine", True)
            self.recovery: Subsystem = Recovery("First stage parachutes", False)
            self.fins: Subsystem = Fins("First stage Fins")
            self.electronics: Subsystem = Electronics("First stage electronics")
            self.shoulder: Subsystem = Shoulder("Shoulder")

    class Stage2(Stage):
        def __init__(self, name: str):
            """
            :param name: Name of the stage
            """
            super().__init__(name, True, False, True)  # General parameters

            # Specific
            self.engine: Subsystem = Engine("Second stage Engine", False)
            self.recovery: Subsystem = Recovery("Second stage Parachutes", True)
            self.fins: Subsystem = Fins("Second stage Fins")
            self.electronics: Subsystem = Electronics("Second stage electronics")
            self.nosecone: Subsystem = Nosecone("Nosecone")
            self.payload: Subsystem = Payload("Scientific Payload")

    def update(self, print_warnings=True):
        # Start with all Rocket parameters at zero
        for key in self.compare_list:
            self[key] = 0

        for stage_key, stage_value in self.__dict__.items():
            if "stage" in stage_key:

                # Start with all Stage parameters at zero
                for key in self.compare_list:
                    self[stage_key][key] = 0

                # Summ all shared Subsystem parameters into Stage parameters
                for subsystem_key, subsystem_value in stage_value.__dict__.items():
                    if isinstance(subsystem_value, Subsystem):
                        for variable_key, variable_value in subsystem_value.__dict__.items():
                            if variable_key in self.compare_list:
                                if variable_key == "dry_mass" and subsystem_key != "engine":  # Dry mass is the same as actual mass for everything except the engine
                                    self[stage_key][subsystem_key].dry_mass = self[stage_key][subsystem_key].mass
                                if variable_value is None:
                                    if print_warnings:
                                        print(Fore.YELLOW + f"\t\tWarning! '{stage_key}.{subsystem_key}.{variable_key}' is None")
                                elif variable_value < 0:
                                    if print_warnings:
                                        print(Fore.YELLOW + f"\t\tWarning! '{stage_key}.{subsystem_key}.{variable_key}' smaller than zero: {variable_value}")
                                else:
                                    self[stage_key][variable_key] += variable_value  # Add all the Subsystems

                # Sum all shared Stage parameters into Rocket parameters
                for variable_key, variable_value in self[stage_key].__dict__.items():
                    if variable_key in self.compare_list:
                        self[variable_key] += variable_value

    def export_all_values(self):
        parameters: dict = {"iteration": str(self.id)}
        for stage_key, stage_value in self.__dict__.items():
            if "stage" in stage_key:
                for subsystem_key, subsystem_value in stage_value.__dict__.items():
                    if isinstance(subsystem_value, Subsystem):
                        for key, value in subsystem_value.__dict__.items():
                            if isinstance(value, Subsystem):
                                for sub_key, sub_value in value.__dict__.items():
                                    parameters[f"{stage_key}.{subsystem_key}.{key}.{sub_key}"] = sub_value
                            else:
                                parameters[f"{stage_key}.{subsystem_key}.{key}"] = value
                    else:
                        parameters[f"{stage_key}.{subsystem_key}"] = subsystem_value
            else:
                parameters[stage_key] = stage_value

        return parameters


if __name__ == "__main__":
    pass
    # test_rocket: Rocket = Rocket()
    # print(test_rocket.stage1.engine.mass)
    # print(test_rocket.stage2.engine.isp)
