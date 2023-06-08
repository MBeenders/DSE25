import numpy as np
from numba import njit


@njit()
def run(flight, gravity, drag, isa, dt: float = 0.1, start_time: float = 0, end_time: float = 1000, coast: bool = False, delay: float = 0):
    mass_rocket: float = flight.mass[0]
    mass_fuel: float = flight.fuel_mass_curve[0]
    mass_total: float = mass_rocket + mass_fuel

    for i, time in enumerate(np.linspace(start_time, end_time, int((end_time-start_time) / dt))):
        if flight.locations[i][1] >= 0:
            # Atmosphere
            flight.temperature[i], flight.pressure[i], flight.density[i] = isa(flight.locations[i][1])

            # Calculate forces
            force_gravity = gravity(flight.locations[i][1], mass_total)
            force_drag = drag(flight, flight.velocities[i], flight.density[i])

            if coast:
                force_thrust: float = 0
                mass_fuel: float = 0
            else:
                if delay <= time < (flight.burn_time + start_time + delay):
                    force_thrust = flight.thrust_curve[i]
                    mass_fuel = flight.fuel_mass_curve[i]
                else:
                    mass_fuel: float = 0
                    force_thrust: float = 0

            # New mass
            mass_total: float = mass_rocket + mass_fuel

            force_x = - force_drag[0] + force_thrust * np.sin(flight.angles[i][0])
            force_y = - force_drag[1] + force_thrust * np.cos(flight.angles[i][0]) - force_gravity
            print(force_y, force_thrust)

            # Iteration
            acceleration = np.array((force_x, force_y), dtype=np.float64) / mass_total
            flight.velocities[i + 1] = acceleration * dt + flight.velocities[i]
            flight.locations[i + 1] = flight.velocities[i] * dt + flight.locations[i]

            total_velocity: float = np.linalg.norm(flight.velocities[i])
            if total_velocity == 0:
                flight.angles[i][0] = 0
            else:
                flight.angles[i][0] = np.arcsin(flight.velocities[i][0] / total_velocity)

            flight.time[i + 1] = time
            time += dt

        else:
            break


if __name__ == '__main__':
    pass
    # run(engine=engines.Solid())
