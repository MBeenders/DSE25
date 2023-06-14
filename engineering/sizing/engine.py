import math
import numpy as np


# ENGINE SIZING FUNCTIONS
g_earth = 9.80665


# computing the initial acceleration dictated by the launch tower length and exit velocity [m/s^2]
def initial_acceleration(length: float, velocity: float) -> float:
    launch_tower_acceleration = velocity ** 2 / (2 * length)
    return launch_tower_acceleration


# computing the amount of thrust based on tower exit velocity [N]
def thrust_force(vehicle_mass, acceleration):
    resultant = vehicle_mass * acceleration
    thrust = resultant + vehicle_mass * g_earth
    return thrust


# computing the effective exhaust velocity based on ProPep outputs [m/s]
def eff_exhaust_velocity(specific_impulse, cc):
    effective_exhaust_velocity = cc * specific_impulse * g_earth
    return effective_exhaust_velocity


# calculating the effective propellant mass [kg]
def propellant_mass(specific_impulse, total_impulse):
    mass_propellant = total_impulse / (specific_impulse * g_earth)
    return mass_propellant


# calculating the mass flow based on ProPep info [kg/s]
def mass_flow(specific_impulse, thrust):
    # mass_p = propellant_mass(Isp, I1, g)
    m_dot = thrust / (specific_impulse * g_earth)
    return m_dot


def casing_thickness(strength, outer_diameter, pressure, liner_thickness):
    wall_thickness = (pressure * outer_diameter) / (2 * strength + 2 * pressure) + liner_thickness
    return wall_thickness


# determining chamber volume. This contains both the propellant volume and the empty port volume
def chamber_volume(mass_propellant, rho, Vl):
    volume_chamber = mass_propellant / (rho * Vl)
    return volume_chamber


def propellant_outer_diameter(stage_diameter, wall_thickness):
    grain_diameter = stage_diameter - 2 * wall_thickness
    return grain_diameter


# determining the chamber length, not including bulkheads, and nozzle
def chamber_length(volume_chamber, grain_diameter):
    length_chamber = (4 * volume_chamber) / (math.pi * grain_diameter ** 2)
    return length_chamber


# determining the nozzle throat area, based on c_star, chamber pressure and massflow
def nozzle_throat_area(mass_flow, c_star, chamber_pressure):
    area_throat = (mass_flow * c_star) / chamber_pressure
    return area_throat


def nozzle_exit_area(pressure_chamber, gamma, pressure_ambient, throat_area):
    p0 = pressure_chamber
    p = pressure_ambient
    k = gamma
    M = np.sqrt(2 / (k - 1) * ((p0 / p) ** ((k - 1) / k) - 1))
    exit_area = throat_area / M * math.sqrt(((1 + (k - 1) / 2 * M ** 2) / (1 + (k - 1) / 2)) ** ((k + 1) / (k - 1)))
    return exit_area


# determining the L/Dt
def length_nozzle(exit_area, throat_area):
    area_ratio = exit_area / throat_area
    nozzle_length = (- 0.0034 * area_ratio ** 2 + 0.3619 * area_ratio + 0.6766) * 2 * math.sqrt(throat_area / math.pi)
    return nozzle_length


# determining the overall length of the motor
def total_length(nozzle_length, length_chamber):
    return nozzle_length + length_chamber


# determining the casing mass
def casing_mass(wall_thickness, stage_diameter, length_chamber, rho_casing):
    chamber_mass = math.pi * ((stage_diameter/2) ** 2 - ((stage_diameter - 2 * wall_thickness)/2) ** 2) * length_chamber * rho_casing
    return chamber_mass


# determining the nozzle mass, based on nozzle length, an assumed thickness and material properties
def nozzle_mass(nozzle_thickness, throat_area, exit_area, rho_nozzle, length_nozzle):
    R = np.sqrt(exit_area / np.pi)
    r = np.sqrt(throat_area / np.pi)
    l = length_nozzle
    t = nozzle_thickness
    nozzle_mass = rho_nozzle * 1 / 3 * math.pi * l * (R ** 2 + R * r + r ** 2 - (R - t) ** 2 - (R - t) * (r - t) - (r - t) ** 2)
    return nozzle_mass


# determining the total solid motor mass: including chamber, nozzle and extra parts, that are assumed based on simplifications
def solid_motor_mass(chamber_mass, nozzle_mass, bulkhead_mass):
    motor_mass = chamber_mass + nozzle_mass + bulkhead_mass
    return motor_mass


# computing the regression rate based on literature chosen constants [mm/s]
# de Saint Robert's burning rate law
def regression_rate(chamber_pressure, pressure_coefficient, pressure_exponent):
    reg_rate = pressure_coefficient * chamber_pressure ** pressure_exponent
    return reg_rate


# computing the propellant burn area
def burn_area(regression_rate, mass_flow, rho):
    prop_burn_area = mass_flow / (regression_rate * rho)
    return prop_burn_area


# Run through all separate calculations
def calculate_engine_specs(engine, ambient_pressure):
    """
    :param engine: Engine subclass of the Rocket class, only one of the two stages.
    :param ambient_pressure: Pressure outside the Engine [Pa].
    Calculates the main specs of the Engine, like propellant_mass, engine length, and engine mass.
    """
    # Calculate propellant mass
    engine.propellant_mass = propellant_mass(engine.isp, engine.impulse)
    engine.mass_flow = mass_flow(engine.isp, engine.thrust)

    # Chamber
    engine.casing_thickness = casing_thickness(engine.yield_strength, engine.diameter, engine.chamber_pressure * engine.safety_factor, engine.liner_thickness)
    engine.chamber_volume = chamber_volume(engine.propellant_mass, engine.propellant_density, engine.volumetric_constant)
    engine.grain_diameter = propellant_outer_diameter(engine.diameter, engine.casing_thickness)
    engine.chamber_length = chamber_length(engine.chamber_volume, engine.grain_diameter)

    # Nozzle
    engine.nozzle_throat_area = nozzle_throat_area(engine.mass_flow, engine.c_star, engine.chamber_pressure)
    engine.nozzle_exit_area = nozzle_exit_area(engine.chamber_pressure, engine.chamber_gamma, ambient_pressure, engine.nozzle_throat_area)
    engine.nozzle_area_ratio = engine.nozzle_exit_area / engine.nozzle_throat_area
    engine.nozzle_length = length_nozzle(engine.nozzle_exit_area, engine.nozzle_throat_area)
    # print(engine.yield_strength, engine.diameter, engine.chamber_pressure, engine.liner_thickness, engine.casing_thickness)

    # Calculate engine mass
    engine.casing_mass = casing_mass(engine.casing_thickness, engine.diameter, engine.chamber_length, engine.casing_density)
    engine.nozzle_mass = nozzle_mass(engine.nozzle_thickness, engine.nozzle_throat_area, engine.nozzle_exit_area, engine.nozzle_density, engine.nozzle_length)

    # Summing
    engine.dry_mass = solid_motor_mass(engine.casing_mass, engine.nozzle_mass, engine.bulkhead_mass)
    engine.mass = engine.dry_mass + engine.propellant_mass
    engine.length = total_length(engine.nozzle_length, engine.chamber_length)


# Mauro's iteration garden
def create_thrust_curve(engine, dt) -> np.array:
    thrust: float = engine.thrust
    return thrust * np.ones(int(engine.burn_time * (1/dt)), dtype=float)


def create_fuel_mass_curve(engine, dt) -> np.array:
    fuel_mass: float = engine.propellant_mass
    return np.linspace(fuel_mass, 0, int(engine.burn_time * (1/dt)), dtype=float)


def create_stage1_engine(rocket):
    # Calculate thrust
    acceleration = initial_acceleration(rocket.stage1.engine.launch_tower_length,
                                        rocket.stage1.engine.launch_exit_velocity)
    rocket.stage1.engine.thrust = thrust_force(rocket.mass, acceleration)

    # Calculate stage1 engine specs
    calculate_engine_specs(rocket.stage1.engine, 41060)

    # Create curves
    rocket.stage1.engine.thrust_curve = create_thrust_curve(rocket.stage1.engine, rocket.simulator.dt)
    rocket.stage1.engine.fuel_mass_curve = create_fuel_mass_curve(rocket.stage1.engine, rocket.simulator.dt)


def create_stage2_engine(rocket):
    # Calculate engine specs with new Thrust
    calculate_engine_specs(rocket.stage2.engine, 41060)

    # Create curves
    rocket.stage2.engine.thrust_curve = create_thrust_curve(rocket.stage2.engine, rocket.simulator.dt)
    rocket.stage2.engine.fuel_mass_curve = create_fuel_mass_curve(rocket.stage2.engine, rocket.simulator.dt)


def stage2_iteration(rocket, apogee_goal):
    # Makes the classes easier to read
    simulator = rocket.simulator
    engine = rocket.stage2.engine

    # Main parameters
    apogee: float = simulator.apogee

    difference = apogee_goal - apogee  # Difference in altitude, negative means an overshoot
    engine.impulse += 0.3 * difference  # Change Impulse to get closer to the target altitude
    engine.thrust = engine.impulse / engine.burn_time

    create_stage2_engine(rocket)

    # Simulate
    simulator.create_stages(rocket)
    simulator.run()
    simulator.delete_stages()
    return difference


def optimize(rocket, max_iterations, apogee_goal, accuracy):
    create_stage1_engine(rocket)  # stage1 engine sizing

    # ToDo: Thrust is calculate

    for i in range(max_iterations):
        difference = stage2_iteration(rocket, apogee_goal)
        if difference < accuracy:
            break


def initialize(rocket):
    create_stage1_engine(rocket)
    create_stage2_engine(rocket)
    return rocket


def run(rocket):
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    optimize(rocket, 30, 90E3, 1)

    # Cost
    rocket.stage1.engine.cost = 0  # Maybe expand?
    rocket.stage2.engine.cost = 0  # Maybe expand?

    return rocket

# if __name__ == "__main__":
#     test_rocket = Rocket()
#     run(test_rocket)
    # # universal constants
    # g = 9.80665  # [m/s^2]
    # cc = rocket[stage].engine.chamber_pressure  # Isp correction factor
    # p = 101325  # ambient pressure [Pa]
    #
    # m_v = rocket.mass  # vehicle mass [kg]
    # Pc = rocket[stage].engine.chamber_pressure  # 7 * 10 ** 6 chamber pressure [Pa]
    #
    # # launch tower properties
    # h = rocket[stage].engine.launch_tower_length  # launch tower length [m]
    # lt_v = rocket[stage].engine.launch_exit_velocity  # required launch tower exit velocity [m/s]
    #
    # # ballistic performance inputs booster
    # F1 = rocket[stage].engine.thrust  # thrust [N]
    # t1 = rocket[stage].engine.burn_time  # duration [s]
    # I1 = rocket[stage].engine.impulse  # impulse [N*s]
    # d1 = rocket[stage].engine.diameter  # diameter first stage [m]
    #
    # # ballistic performance inputs sustainer
    # F2 = 1000  # thrust [N]
    # t2 = 2  # duration [s]
    # I2 = 40000  # impulse [N*s]
    # d2 = 0.15  # diameter second stage [m]
    #
    # # ProPep inputs
    # Isp = 220  # specific impulse [s]
    # c_star = 1000  # characteristic exhaust velocity c* [m/s]
    # rho = 1700  # propellant density [kg/m^3]
    # m = 100  # molecular weight [?]
    # gamma = 1.4  # chamber gamma []
    # Tc = 3000  # chamber temperature [K]
    #
    # # sizing constants
    # Vl = 0.8  # NASA said so; volumetric constant
    #
    # tower_acc = initial_acceleration(h, lt_v)
    # thrust = thrust_force(m_v, tower_acc)
    # mass_propellant = propellant_mass(Isp, I1, g)
    # m_dot = mass_flow(Isp, g, thrust)
    # # engine casing calculations
    #
    # # computing the yielding constrained wall thickness, based on the yield strength of alu 6082, and outside stage diameter
    # yield_strength = 6000000  # look this up for our material
    # safety_factor = 1.5
    # pressure_yield = safety_factor * Pc
    #
    # liner_thickness = 0.003  # charlie made me do it [m]
    # wall_thickness = casing_thickness(yield_strength, d1, Pc, liner_thickness)
    # volume_chamber = chamber_volume(mass_propellant, rho, Vl)
    # grain_diameter = propellant_outer_diameter(d1, wall_thickness)
    # length_chamber = chamber_length(volume_chamber, grain_diameter)
    #
    # throat_area = nozzle_throat_area(m_dot, c_star, Pc)
    # area_exit = 4
    # area_ratio = area_exit / throat_area
    #
    # nozzle_length = length_nozzle(area_ratio, throat_area)
    #
    # length_motor = total_length(nozzle_length, length_chamber)
    #
    # # VALIDATION RELEVANT COMPUTATIONS
    #
    # # figuring out the regression rate stuff
    # # asumptions (estimated based on literature)
    # a = 1  # coefficient of pressure. chosen from literature
    # n = 2  # pressure exponent. chosen from literature
