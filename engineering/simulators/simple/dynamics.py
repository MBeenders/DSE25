import numpy as np
from numba import njit


@njit()
def run(flight, gravity, drag, isa, dt: float = 0.1, start_time: float = 0, end_time: float = 100):
    mass_rocket: float = 50
    mass_fuel: float = 100
    mass_total: float = mass_rocket + mass_fuel

    for i, time in enumerate(np.linspace(start_time, end_time, int((end_time-start_time) / dt))):
        if flight.locations[i][1] >= 0:
            # Atmosphere
            flight.temperature[i], flight.pressure[i], flight.density[i] = isa(flight.locations[i][1])

            # Calculate forces
            force_gravity = gravity(flight.locations[i][1], mass_total)
            force_drag = drag(flight, flight.velocities[i], flight.density[i])
            force_thrust = flight.thrust_curve[i]
            mass_fuel = flight.fuel_mass[i]

            # New mass
            mass_total: float = mass_rocket + mass_fuel
            total_velocity: float = np.linalg.norm(flight.velocities[i])

            force_x = - force_drag[0] + force_thrust * flight.velocities[i][0] / total_velocity
            force_y = - force_drag[1] + force_thrust * flight.velocities[i][1] / total_velocity - force_gravity

            # Iteration
            acceleration = np.array((force_x, force_y), dtype=np.float64) / mass_total
            flight.velocities[i + 1] = acceleration * dt + flight.velocities[i]
            flight.locations[i + 1] = flight.velocities[i] * dt + flight.locations[i]

            time += dt

        else:
            break


if __name__ == '__main__':
    pass
    # run(engine=engines.Solid())
