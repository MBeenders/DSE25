import numpy as np
from numba import njit


#@njit()
def run(flight, stage: int, gravity, drag, isa, dt: float = 0.1, start_time: float = 0, end_time: float = 1000, coast: bool = False, delay: float = 0):
    mass_rocket: float = flight.mass[0]
    mass_fuel: float = flight.fuel_mass_curve[0]
    mass_total: float = mass_rocket + mass_fuel

    delay_i: float = 0

    for i, time in enumerate(np.linspace(start_time, end_time, int((end_time-start_time) / dt))):
        if flight.velocities[i][1] >= 0:
            # Atmosphere
            flight.temperature[i], flight.pressure[i], flight.density[i] = isa(flight.locations[i][1])
            flight.speed_of_sound[i] = np.sqrt(1.4 * 287 * flight.temperature[i])

            # Calculate forces
            force_gravity = gravity(flight.locations[i][1], mass_total)
            force_drag = drag(flight, flight.total_velocities[i][0], flight.temperature[i], flight.density[i], stage)

            if coast:
                force_thrust: float = 0
                mass_fuel: float = 0
            else:
                if (start_time + delay) > time:
                    mass_fuel: float = flight.fuel_mass_curve[0]
                    force_thrust: float = 0
                elif (start_time + delay) <= time < (flight.burn_time + start_time + delay - dt):
                    delay_i += 1
                    force_thrust = flight.thrust_curve[delay_i]
                    mass_fuel = flight.fuel_mass_curve[delay_i]
                else:
                    mass_fuel: float = 0
                    force_thrust: float = 0

            # New mass
            mass_total: float = mass_rocket + mass_fuel

            force_x = (force_thrust - force_drag) * np.sin(flight.angles[i][0])
            force_y = (force_thrust - force_drag) * np.cos(flight.angles[i][0]) - force_gravity

            # Append forces to flight
            flight.force_drag[i] = force_drag
            flight.force_thrust[i] = force_thrust
            flight.force_gravity[i] = force_gravity

            # Iteration
            acceleration = np.array((force_x, force_y), dtype=np.float64) / mass_total
            flight.velocities[i + 1] = acceleration * dt + flight.velocities[i]
            flight.locations[i + 1] = flight.velocities[i] * dt + flight.locations[i]

            total_velocity: float = np.linalg.norm(flight.velocities[i])
            flight.total_velocities[i + 1] = total_velocity
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
