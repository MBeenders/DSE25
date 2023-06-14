from numba.experimental import jitclass
from numba import int32, float32
import numpy as np


# @njit()
# def solid_1(time: float) -> tuple[float, float]:
#     mass_fuel: float = 100
#     burn_time: float = 100  # s
#     burn_rate: float = 1  # kg/s
#     if time < burn_time:
#         thrust = 10000  # N
#         return thrust, mass_fuel - burn_rate
#     else:
#         return 0, mass_fuel

spec = [("mass_fuel", float32),
        ("burn_time", float32),
        ("burn_rate", float32),
        ("thrust", float32)]


@jitclass(spec)
class Engine:
    def __init__(self):
        self.mass_fuel: float = 100  # kg
        self.burn_time: float = 10  # s
        self.burn_rate: float = self.mass_fuel / self.burn_time  # kg/s

        self.thrust: float = 10000  # N

    def burn(self, dt: float):
        if self.mass_fuel > 0:
            self.mass_fuel -= self.burn_rate * dt
            if self.mass_fuel > 0:
                return self.thrust, self.mass_fuel
            else:
                return self.thrust, 0
        else:
            return 0, self.mass_fuel
