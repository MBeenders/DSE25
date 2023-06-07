from numba import njit
from numba.experimental import jitclass
from numba import int32, float64
import numpy as np

from simple.dynamics import run as dynamics_run
from simple.engines import Engine
from simple.gravity import gravity
from simple.aerodynamics import drag, isa

rocket_specs = [("max_iterations", int32),
                ("locations", float64[:, :]),
                ("velocities", float64[:, :]),
                ("pressure", float64[:]),
                ("temperature", float64[:]),
                ("density", float64[:])]


@jitclass(rocket_specs)
class RocketData:
    def __init__(self, max_iterations: int):
        # Dynamics
        self.locations: np.array = np.zeros((max_iterations, 2), float64)
        self.velocities: np.array = np.zeros((max_iterations, 2), float64)

        # Atmosphere
        self.pressure: np.array = np.zeros(max_iterations, float64)
        self.temperature: np.array = np.zeros(max_iterations, float64)
        self.density: np.array = np.zeros(max_iterations, float64)


class Simulator:
    def __init__(self):
        self.apogee: float = 0
        self.rocket: RocketData = RocketData(10000)
        self.engine: Engine = Engine()

    def run(self):
        self.rocket.velocities[0][1] = 10E-5
        dynamics_run(self.rocket, self.engine, gravity, drag, isa)
        self.trim_lists()

    def trim_lists(self):
        self.rocket.locations = self.rocket.locations[~np.all(self.rocket.locations == 0, axis=1)]
        self.rocket.velocities = self.rocket.velocities[~np.all(self.rocket.velocities == 0, axis=1)]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]


if __name__ == "__main__":
    sim = Simulator()
    sim.run()
