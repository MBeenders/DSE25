from numba import njit
from numba.experimental import jitclass
from numba import int32, float64
import numpy as np


rocket_specs = [("max_iterations", int32),
                ("locations", float64[:, :]),
                ("velocities", float64[:, :]),
                ("angles", float64[:, :]),
                ("mass", float64[:]),
                ("cd", float64),
                ("diameter", float64),
                ("thrust_curve", float64[:]),
                ("fuel_mass", float64[:]),
                ("mmoi", float64[:]),
                ("pressure", float64[:]),
                ("temperature", float64[:]),
                ("density", float64[:])]


@jitclass(rocket_specs)
class FlightData:
    def __init__(self, max_iterations: int):
        # Dynamics
        self.locations: np.array = np.zeros((max_iterations, 2), float64)
        self.velocities: np.array = np.zeros((max_iterations, 2), float64)
        self.angles: np.array = np.zeros((max_iterations, 1), float64)

        # General properties
        self.mass: np.array = np.zeros(max_iterations, float64)
        self.cd: float64 = 0.65
        self.diameter: float64 = 0.15

        # Engine
        self.thrust_curve: np.array = np.zeros(max_iterations, float64)  # Thrust curve
        self.fuel_mass: np.array = np.zeros(max_iterations, float64)  # Total Engine mass over time
        self.mmoi: np.array = np.zeros(max_iterations, float64)  # MMOI over time

        # Atmosphere
        self.pressure: np.array = np.zeros(max_iterations, float64)
        self.temperature: np.array = np.zeros(max_iterations, float64)
        self.density: np.array = np.zeros(max_iterations, float64)


class Simulator:
    def __init__(self, mission_profile: dict, dynamics_run, gravity, drag, isa):
        # Functions
        self.dynamics_run = dynamics_run
        self.gravity = gravity
        self.drag = drag
        self.isa = isa

        # Values
        self.apogee: float = 0
        self.stages: dict = {}
        self.mission_profile: dict = mission_profile

    def run(self):
        self.stages["Total"].velocities[0][1] = 10E-5
        self.dynamics_run(self.stages["Total"], self.gravity, self.drag, self.isa)
        self.trim_lists(self.stages["Total"])

    def create_stages(self, rocket):
        if self.mission_profile["stages"] == 2:
            # Total stage
            self.stages["Total"] = FlightData(10000)
            self.stages["Total"].mass[0] = rocket.mass
            self.stages["Total"].cd = rocket.cd
            self.stages["Total"].diameter = rocket.diameter
            self.stages["Total"].thrust_curve = rocket.stage1.engine.thrust_curve
            self.stages["Total"].fuel_mass = rocket.stage1.engine.fuel_mass
            self.stages["Total"].mmoi = rocket.stage1.engine.mmoi

            # Separation
            # Stage 1
            self.stages["Stage1"] = FlightData(10000)
            self.stages["Stage1"].mass[0] = rocket.stage1.mass

            # Stage 2
            self.stages["Stage2"] = FlightData(10000)
            self.stages["Stage2"].mass[0] = rocket.stage2.mass
            self.stages["Stage2"].thrust_curve = rocket.stage2.engine.thrust_curve
            self.stages["Stage2"].fuel_mass = rocket.stage2.engine.fuel_mass
            self.stages["Stage2"].mmoi = rocket.stage2.engine.mmoi
        else:
            raise ModuleNotFoundError("Only 2-Stage rockets are supported atm")

    @staticmethod
    def trim_lists(rocket: FlightData):
        rocket.locations = rocket.locations[~np.all(rocket.locations == 0, axis=1)]
        rocket.velocities = rocket.velocities[~np.all(rocket.velocities == 0, axis=1)]

    def insert_engine(self, engine):
        pass

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


if __name__ == "__main__":
    profile = {"stages": 2,
               "launch": {"exact", 0},
               "engine1_ignition": {"exact", 0},
               "engine2_ignition": {"delay", 2},
               "separation": {"delay", 1}
               }

    sim = Simulator(profile)
