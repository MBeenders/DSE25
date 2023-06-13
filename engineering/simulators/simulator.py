from numba import njit
from numba.experimental import jitclass
from numba import int32, float64
import matplotlib.pyplot as plt
import numpy as np


rocket_specs = [("max_iterations", int32),
                ("time", float64[:]),
                ("locations", float64[:, :]),
                ("velocities", float64[:, :]),
                ("angles", float64[:, :]),
                ("total_velocities", float64[:, :]),
                ("speed_of_sound", float64[:]),
                ("mass", float64[:]),
                ("cd", float64),
                ("diameter", float64),
                ("diameter1", float64),
                ("diameter2", float64),
                ("shoulder_length", float64),
                ("drag_coefficient_nosecone", float64),
                ("fineness_ratio", float64),
                ("joint_angle", float64),
                ("wetted_area", float64),
                ("wetted_area_body", float64),
                ("wetted_area_fins1", float64),
                ("wetted_area_fins2", float64),
                ("fin_thickness1", float64),
                ("fin_thickness2", float64),
                ("fin_mac1", float64),
                ("fin_mac2", float64),
                ("fin_span1", float64),
                ("fin_span2", float64),
                ("thrust_curve", float64[:]),
                ("fuel_mass_curve", float64[:]),
                ("mmoi", float64[:]),
                ("burn_time", float64),
                ("pressure", float64[:]),
                ("temperature", float64[:]),
                ("density", float64[:]),
                ("force_drag", float64[:]),
                ("force_thrust", float64[:]),
                ("force_gravity", float64[:])]


@jitclass(rocket_specs)
class FlightData:
    def __init__(self, max_iterations: int):
        # Dynamics
        self.time: np.array = np.zeros(max_iterations, float64)
        self.locations: np.array = np.zeros((max_iterations, 2), float64)
        self.velocities: np.array = np.zeros((max_iterations, 2), float64)
        self.angles: np.array = np.zeros((max_iterations, 1), float64)

        self.total_velocities: np.array = np.zeros((max_iterations, 2), float64)
        self.speed_of_sound: np.array = np.zeros(max_iterations, float64)

        # General properties
        self.mass: np.array = np.zeros(max_iterations, float64)
        self.cd: float64 = 0
        self.diameter: float64 = 0

        # Advanced Area specs
        self.diameter1: float64 = 0  # Diameter Stage 1
        self.diameter2: float64 = 0  # Diameter Stage 2

        self.shoulder_length: float64 = 0

        self.drag_coefficient_nosecone: float64 = 0
        self.fineness_ratio: float64 = 0
        self.joint_angle: float64 = 0

        self.wetted_area: float64 = 0  # Total wetted area of Stage 2
        self.wetted_area_body: float64 = 0  # Excludes the Nosecone (Should it?)

        self.wetted_area_fins1: float64 = 0
        self.wetted_area_fins2: float64 = 0
        self.fin_thickness1: float64 = 0
        self.fin_thickness2: float64 = 0
        self.fin_mac1: float64 = 0
        self.fin_mac2: float64 = 0
        self.fin_span1: float64 = 0
        self.fin_span2: float64 = 0

        # Engine
        self.thrust_curve: np.array = np.zeros(max_iterations, float64)  # Thrust curve
        self.fuel_mass_curve: np.array = np.zeros(max_iterations, float64)  # Total Engine mass over time
        self.mmoi: np.array = np.zeros(max_iterations, float64)  # MMOI over time
        self.burn_time: float64 = 0

        # Atmosphere
        self.pressure: np.array = np.zeros(max_iterations, float64)
        self.temperature: np.array = np.zeros(max_iterations, float64)
        self.density: np.array = np.zeros(max_iterations, float64)

        # Forces
        self.force_drag: np.array = np.zeros(max_iterations, float64)
        self.force_thrust: np.array = np.zeros(max_iterations, float64)
        self.force_gravity: np.array = np.zeros(max_iterations, float64)


class Simulator:
    def __init__(self, mission_profile: dict, simulator_parameters: dict, dynamics_run, gravity, drag, isa):
        self.dt: float64 = simulator_parameters["dt"]  # [s]
        self.maximum_iterations = int(simulator_parameters["maximum_iterations"])

        # Functions
        self.dynamics_run = dynamics_run
        self.gravity = gravity
        self.drag = drag
        self.isa = isa

        # Curves (Total Stage to 2nd Stage after separation)
        self.times: np.array = np.zeros(self.maximum_iterations, dtype=float)  # List with all th time stamps

        self.altitudes: np.array = np.zeros(self.maximum_iterations, dtype=float)
        self.velocities: np.array = np.zeros(self.maximum_iterations, dtype=float)
        self.speed_of_sound: np.array = np.zeros(self.maximum_iterations, dtype=float)

        # Values
        self.apogee: float = 0

        self.max_velocity1: float = 0
        self.max_velocity2: float = 0
        self.max_velocity_tot: float = 0

        self.min_speed_of_sound1: float = 0
        self.min_speed_of_sound2: float = 0
        self.min_speed_of_sound_tot: float = 0

        # Mission
        self.stages: dict = {}  # Flight data of the different stages
        self.mission_profile: dict = mission_profile
        self.run_parameters: dict = simulator_parameters

    def run(self):
        if self.mission_profile["stages"] == 2:
            # ToDo: Launch Tower

            # Boost Phase
            end_time = self.stages["Total"].burn_time + self.mission_profile["separation"]["delay"]
            self.dynamics_run(self.stages["Total"], 0, self.gravity, self.drag, self.isa, end_time=end_time, dt=self.dt)
            self.trim_lists(self.stages["Total"])

            # Separation Phase
            start_time = self.stages["Total"].time[-1]

            self.stages["Stage2"].time[0] = self.stages["Total"].time[-1]
            self.stages["Stage2"].locations[0] = self.stages["Total"].locations[-1]
            self.stages["Stage2"].velocities[0] = self.stages["Total"].velocities[-1]
            self.stages["Stage2"].angles[0] = self.stages["Total"].angles[-1]

            self.dynamics_run(self.stages["Stage2"], 2, self.gravity, self.drag, self.isa, start_time=start_time, dt=self.dt, delay=self.mission_profile["engine2_ignition"]["delay"])
            self.trim_lists(self.stages["Stage2"])

            self.update()

        else:
            raise ModuleNotFoundError("Only 2-Stage rockets are supported atm")

    def create_stages(self, rocket, show_params=True):
        if self.mission_profile["stages"] == 2:
            # Total stage
            self.stages["Total"] = FlightData(int(self.maximum_iterations))
            self.stages["Total"].mass[0] = rocket.mass
            self.stages["Total"].cd = rocket.cd
            self.stages["Total"].diameter = rocket.diameter
            self.stages["Total"].diameter1 = rocket.stage1.diameter
            self.stages["Total"].diameter2 = rocket.stage2.diameter
            self.stages["Total"].shoulder_length = rocket.stage1.shoulder.length
            self.stages["Total"].drag_coefficient_nosecone = rocket.stage2.nosecone.drag_coefficient
            self.stages["Total"].fineness_ratio = rocket.fineness_ratio
            self.stages["Total"].joint_angle = rocket.stage2.nosecone.joint_angle
            self.stages["Total"].wetted_area = rocket.wetted_area
            self.stages["Total"].wetted_area_body = rocket.wetted_area - rocket.stage1.fins.wetted_area - rocket.stage2.fins.wetted_area
            self.stages["Total"].wetted_area_fins1 = rocket.stage1.fins.wetted_area
            self.stages["Total"].wetted_area_fins2 = rocket.stage2.fins.wetted_area
            self.stages["Total"].fin_thickness1 = rocket.stage1.fins.thickness
            self.stages["Total"].fin_thickness2 = rocket.stage2.fins.thickness
            self.stages["Total"].fin_mac1 = rocket.stage1.fins.mac
            self.stages["Total"].fin_mac2 = rocket.stage2.fins.mac
            self.stages["Total"].fin_span1 = rocket.stage1.fins.span
            self.stages["Total"].fin_span2 = rocket.stage2.fins.span
            self.stages["Total"].thrust_curve = rocket.stage1.engine.thrust_curve
            self.stages["Total"].fuel_mass_curve = rocket.stage1.engine.fuel_mass_curve
            self.stages["Total"].mmoi = rocket.stage1.engine.mmoi
            self.stages["Total"].burn_time = rocket.stage1.engine.burn_time

            # Separation
            # Stage 1
            self.stages["Stage1"] = FlightData(int(self.maximum_iterations))
            self.stages["Stage1"].mass[0] = rocket.stage1.mass

            # Stage 2
            self.stages["Stage2"] = FlightData(int(self.maximum_iterations))
            self.stages["Stage2"].mass[0] = rocket.stage2.mass
            self.stages["Stage2"].cd = rocket.stage2.cd
            self.stages["Stage2"].diameter = rocket.stage2.diameter
            self.stages["Stage2"].diameter2 = rocket.stage2.diameter
            self.stages["Stage2"].drag_coefficient_nosecone = rocket.stage2.nosecone.drag_coefficient
            self.stages["Stage2"].fineness_ratio = rocket.fineness_ratio
            self.stages["Stage2"].joint_angle = rocket.stage2.nosecone.joint_angle
            self.stages["Stage2"].wetted_area = rocket.stage2.wetted_area
            self.stages["Stage2"].wetted_area_body = rocket.stage2.wetted_area - rocket.stage2.fins.wetted_area
            self.stages["Stage2"].wetted_area_fins2 = rocket.stage2.fins.wetted_area
            self.stages["Stage2"].fin_thickness2 = rocket.stage2.fins.thickness
            self.stages["Stage2"].fin_mac2 = rocket.stage2.fins.mac
            self.stages["Stage2"].fin_span2 = rocket.stage2.fins.span
            self.stages["Stage2"].thrust_curve = rocket.stage2.engine.thrust_curve
            self.stages["Stage2"].fuel_mass_curve = rocket.stage2.engine.fuel_mass_curve
            self.stages["Stage2"].mmoi = rocket.stage2.engine.mmoi
            self.stages["Stage2"].burn_time = rocket.stage2.engine.burn_time
        else:
            raise ModuleNotFoundError("Only 2-Stage rockets are supported atm")

    def combine_lists(self):
        self.times = np.concatenate((self.stages["Total"].time, self.stages["Stage2"].time), axis=0)
        self.altitudes = np.concatenate((self.stages["Total"].locations.transpose()[1],
                                         self.stages["Stage2"].locations.transpose()[1]), axis=0)
        self.velocities = np.concatenate((self.stages["Total"].velocities.transpose()[1],
                                          self.stages["Stage2"].velocities.transpose()[1]), axis=0)
        self.speed_of_sound = np.concatenate((self.stages["Total"].speed_of_sound.transpose(),
                                              self.stages["Stage2"].speed_of_sound.transpose()), axis=0)

    def update(self):
        self.combine_lists()
        self.apogee = self.stages["Stage2"].locations.transpose()[1].max()

        for name, stage in self.stages.items():
            if name == "Total":
                self.max_velocity_tot = self.stages["Total"].velocities.transpose()[1].max()
                self.min_speed_of_sound_tot = self.stages["Total"].speed_of_sound.transpose().max()
            elif name == "Stage1":
                self.max_velocity1 = self.stages["Stage1"].velocities.transpose()[1].max()
                self.min_speed_of_sound1 = self.stages["Stage1"].speed_of_sound.transpose().max()
            elif name == "Stage2":
                self.max_velocity2 = self.stages["Stage2"].velocities.transpose()[1].max()
                self.min_speed_of_sound2 = self.stages["Stage2"].speed_of_sound.transpose().max()
            else:
                print(f"\t\t'{name}' not implemented")

    @staticmethod
    def trim_lists(rocket: FlightData):
        rocket.time = rocket.time[rocket.time != 0]
        rocket.locations = rocket.locations[~np.all(rocket.locations == 0, axis=1)]
        rocket.velocities = rocket.velocities[~np.all(rocket.velocities == 0, axis=1)]

    def plot_trajectory(self):
        self.combine_lists()
        plt.plot(self.times, self.altitudes)
        plt.show()

        plt.plot(self.times, self.velocities[:-1])
        plt.show()

    def delete_stages(self):
        self.stages: dict = {}

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


if __name__ == "__main__":
    pass
