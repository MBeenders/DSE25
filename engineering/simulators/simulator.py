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
                ("mass", float64[:]),
                ("cd", float64),
                ("diameter", float64),
                ("thrust_curve", float64[:]),
                ("fuel_mass_curve", float64[:]),
                ("mmoi", float64[:]),
                ("burn_time", float64),
                ("pressure", float64[:]),
                ("temperature", float64[:]),
                ("density", float64[:])]


@jitclass(rocket_specs)
class FlightData:
    def __init__(self, max_iterations: int):
        # Dynamics
        self.time: np.array = np.zeros(max_iterations, float64)
        self.locations: np.array = np.zeros((max_iterations, 2), float64)
        self.velocities: np.array = np.zeros((max_iterations, 2), float64)
        self.angles: np.array = np.zeros((max_iterations, 1), float64)

        self.total_velocities: np.array = np.zeros((max_iterations, 2), float64)

        # General properties
        self.mass: np.array = np.zeros(max_iterations, float64)
        self.cd: float64 = 0
        self.diameter: float64 = 0

        # Engine
        self.thrust_curve: np.array = np.zeros(max_iterations, float64)  # Thrust curve
        self.fuel_mass_curve: np.array = np.zeros(max_iterations, float64)  # Total Engine mass over time
        self.mmoi: np.array = np.zeros(max_iterations, float64)  # MMOI over time
        self.burn_time: float64 = 0

        # Atmosphere
        self.pressure: np.array = np.zeros(max_iterations, float64)
        self.temperature: np.array = np.zeros(max_iterations, float64)
        self.density: np.array = np.zeros(max_iterations, float64)


class Simulator:
    def __init__(self, mission_profile: dict, dynamics_run, gravity, drag, isa):
        self.dt: float64 = 0.01  # [s]

        # Functions
        self.dynamics_run = dynamics_run
        self.gravity = gravity
        self.drag = drag
        self.isa = isa

        # Values
        self.apogee: float = 0
        self.max_velocity: float = 0

        # Mission
        self.stages: dict = {}  # Flight data of the different stages
        self.mission_profile: dict = mission_profile

    def run(self):
        if self.mission_profile["stages"] == 2:
            # ToDo: Launch Tower

            # Boost Phase
            end_time = self.stages["Total"].burn_time + self.mission_profile["separation"]["delay"]
            self.dynamics_run(self.stages["Total"], self.gravity, self.drag, self.isa, end_time=end_time, dt=self.dt)
            self.trim_lists(self.stages["Total"])

            # Separation Phase
            start_time = self.stages["Total"].time[-1]

            self.stages["Stage2"].time[0] = self.stages["Total"].time[-1]
            self.stages["Stage2"].locations[0] = self.stages["Total"].locations[-1]
            self.stages["Stage2"].velocities[0] = self.stages["Total"].velocities[-1]
            self.stages["Stage2"].angles[0] = self.stages["Total"].angles[-1]

            self.dynamics_run(self.stages["Stage2"], self.gravity, self.drag, self.isa, start_time=start_time, dt=self.dt, delay=self.mission_profile["engine2_ignition"]["delay"])
            self.trim_lists(self.stages["Stage2"])

            self.update()

        else:
            raise ModuleNotFoundError("Only 2-Stage rockets are supported atm")

    def create_stages(self, rocket):
        if self.mission_profile["stages"] == 2:
            # Total stage
            self.stages["Total"] = FlightData(int(10E5))
            self.stages["Total"].mass[0] = rocket.mass
            self.stages["Total"].cd = rocket.cd
            self.stages["Total"].diameter = rocket.diameter
            self.stages["Total"].thrust_curve = rocket.stage1.engine.thrust_curve
            self.stages["Total"].fuel_mass_curve = rocket.stage1.engine.fuel_mass_curve
            self.stages["Total"].mmoi = rocket.stage1.engine.mmoi
            self.stages["Total"].burn_time = rocket.stage1.engine.burn_time

            # Separation
            # Stage 1
            self.stages["Stage1"] = FlightData(int(10E5))
            self.stages["Stage1"].mass[0] = rocket.stage1.mass

            # Stage 2
            self.stages["Stage2"] = FlightData(int(10E5))
            self.stages["Stage2"].mass[0] = rocket.stage2.mass
            self.stages["Stage2"].cd = rocket.stage2.cd
            self.stages["Stage2"].diameter = rocket.stage2.diameter
            self.stages["Stage2"].thrust_curve = rocket.stage2.engine.thrust_curve
            self.stages["Stage2"].fuel_mass_curve = rocket.stage2.engine.fuel_mass_curve
            self.stages["Stage2"].mmoi = rocket.stage2.engine.mmoi
            self.stages["Stage2"].burn_time = rocket.stage2.engine.burn_time
        else:
            raise ModuleNotFoundError("Only 2-Stage rockets are supported atm")

    def update(self):
        self.apogee = self.stages["Stage2"].locations.transpose()[1].max()
        self.max_velocity = self.stages["Stage2"].velocities.transpose()[1].max()

    @staticmethod
    def trim_lists(rocket: FlightData):
        rocket.time = rocket.time[rocket.time != 0]
        rocket.locations = rocket.locations[~np.all(rocket.locations == 0, axis=1)]
        rocket.velocities = rocket.velocities[~np.all(rocket.velocities == 0, axis=1)]

    def combine_lists(self):
        times = np.concatenate((self.stages["Total"].time, self.stages["Stage2"].time), axis=0)
        altitudes = np.concatenate((self.stages["Total"].locations.transpose()[1],
                                    self.stages["Stage2"].locations.transpose()[1]), axis=0)
        velocities = np.concatenate((self.stages["Total"].velocities.transpose()[1],
                                     self.stages["Stage2"].velocities.transpose()[1]), axis=0)

        return times, altitudes, velocities

    def plot_trajectory(self):
        times, altitudes, velocities = self.combine_lists()
        plt.plot(times, altitudes)
        plt.show()

        plt.plot(times, velocities[:-1])
        plt.show()

    def delete_stages(self):
        self.stages: dict = {}

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


if __name__ == "__main__":
    pass
