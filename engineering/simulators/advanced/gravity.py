from numba import njit
import numpy as np


@njit()
def gravity(height, rocket_mass):
    earth_radius: float = 6.371E6  # m
    earth_mass: float = 5.972E24  # kg
    gravitational_constant: float = 6.6743E-11  # m^3 kg^-1 s^-2

    return (gravitational_constant * earth_mass * rocket_mass) / ((earth_radius + height)**2)
