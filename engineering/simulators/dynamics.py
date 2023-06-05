import numpy as np
from numba import njit
from gravity import gravity
from aerodynamics import drag
import engines


@njit()
def run(engine, dt: float = 0.1, start_time: float = 0, end_time: float = 100):
    location: np.ndarray = np.zeros(2, dtype=float)
    velocity: np.ndarray = np.zeros(2, dtype=float)
    velocity[1] = 10**(-10)

    mass_rocket: float = 50
    mass_fuel: float = 100
    mass_total: float = mass_rocket + mass_fuel

    for time in np.linspace(start_time, end_time, int((end_time-start_time) / dt)):
        if location[1] >= 0:
            # Calculate forces
            force_gravity = gravity(location[1], mass_total)
            force_drag = drag(velocity, location[1])
            force_thrust, mass_fuel = engine.burn(dt)

            # New mass
            mass_total: float = mass_rocket + mass_fuel

            total_velocity: float = np.linalg.norm(velocity)

            force_x = - force_drag[0] + force_thrust * velocity[0]/total_velocity
            force_y = - force_drag[1] + force_thrust * velocity[1]/total_velocity - force_gravity

            # Iteration
            acceleration = np.array((force_x, force_y), dtype=float) / mass_total
            velocity += acceleration * dt
            location += velocity * dt

            time += dt

        else:
            break


if __name__ == '__main__':
    run(engine=engines.Solid())
