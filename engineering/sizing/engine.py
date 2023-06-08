from engineering.sizing.rocket import Rocket
import math

#universal constants 
g = 9.80665  #[m/s^2]
cc = 0.95    #Isp correction factor
p = 101325   #ambient pressure [Pa]

m_v = 140   #vehicle mass [kg]
Pc = 7 * 10 ** 6 #chamber pressure [Pa]

#launch tower properties
h = 14      #launch tower length [m]
lt_v = 40   #required launch tower exit velocity [m/s]

#ballistic performance inputs booster
F1 = 1000     #thrust [N]
t1 = 2        #duration [s]
I1 = 120000    #impulse [N*s]
d1 = 0.25      #diameter first stage [m]
wall_thickness1 = 0.2 #casing thickness booster [m]

#ballistic performance inputs sustainer
F2 = 1000     #thrust [N]
t2 = 2        #duration [s]
I2 = 40000    #impulse [N*s]
d2 = 0.15      #diameter second stage [m]
wall_thickness2 = 0.2 #casing thickness sustainer [m]

#ProPep inputs
Isp = 220    #specific impulse [s]
c_star = 1000     #characteristic exhaust velocity c* [m/s]
rho = 1700   #propellant density [kg/m^3]
m = 100      #molecular weight [?]
gamma = 1.4  #chamber gamma []
Tc = 3000    #chamber temperature [K]

#sizing constants
Vl = 0.8    #NASA said so; volumetric constant

#ENGINE SIZING FUNCTIONS

#computing the initial acceleration dictated by the launch tower lenght and exit velocity [m/s^2]
def initial_acc(length, velocity):
    launch_tower_acceleration = velocity**2 / (2 * length)
    return launch_tower_acceleration

tower_acc = initial_acc(h, lt_v)

#computing the amount of thrust based on tower exit velocity [N]
def thrust_force(vehicle_mass, acceleration):
    thrust = vehicle_mass * acceleration
    return thrust

thrust = thrust_force(m_v,tower_acc)

#computing the effective exhaust velocity based on ProPep outputs [m/s]
def eff_exhaust_velocity(specific_impulse, g_earth):
    effective_exhaust_velocity = cc * specific_impulse * g_earth
    return effective_exhaust_velocity

#calculating the effective propellant mass [kg]
def propellant_mass(specific_impulse, total_impulse, g_earth):
    mass_propellant = total_impulse / (specific_impulse * g_earth)
    return mass_propellant

mass_propellant = propellant_mass(Isp, I1, g)

#calculating the mass flow based on ProPep info [kg/s]
def mass_flow(specific_impulse, g_earth, thrust):
    #mass_p = propellant_mass(Isp, I1, g)
    m_dot = thrust / (specific_impulse * g_earth)
    return m_dot

m_dot = mass_flow(Isp, g, thrust)
#engine casing calculations

#computing the yielding constrained wall thickness, based on the yield strength of alu 6082, and outside stage diameter
yield_strength = 6000000  #look this up for our material
safety_factor = 1.5
pressure_yield = safety_factor * Pc

liner_thickness = 0.003 #charlie made me do it [m]


def casing_thickness(strength, outer_diameter, pressure):
    wall_thickness = (pressure * outer_diameter) / (2 * strength + 2 * pressure) + liner_thickness
    return wall_thickness

wall_thickness = casing_thickness(yield_strength, d1, Pc)

#determining chamber volume. This contains both the propellant volume and the empty port volume
def chamber_volume(mass_propellant, rho):
    volume_chamber = mass_propellant / (rho * Vl)
    return volume_chamber

volume_chamber = chamber_volume(mass_propellant, rho)

def propellant_outer_diameter(stage_diameter, wall_thickness):
    grain_diameter = stage_diameter - 2 * wall_thickness
    return grain_diameter

grain_diameter = propellant_outer_diameter(d1, wall_thickness)

#determining the chamber length, not including bulkheads, and nozzle
def chamber_length(volume_chamber, grain_diameter):
    length_chamber = (4 * volume_chamber) / (math.pi * grain_diameter ** 2)
    return length_chamber

length_chamber = chamber_length(volume_chamber, grain_diameter)

#determining the nozzle throat area, based on c_star, chamber pressure and massflow
def nozzle_throat_area(mass_flow, c_star, chamber_pressure):
    area_throat = (mass_flow * c_star) / chamber_pressure
    return area_throat

throat_area = nozzle_throat_area(m_dot, c_star, Pc)
area_exit = 4
area_ratio = area_exit / throat_area

#determining the L/Dt
def length_nozzle(area_ratio, throat_area):
    nozzle_length = (- 0.0034 * area_ratio**2 + 0.3619 * area_ratio + 0.6766) * 2 * math.sqrt(throat_area / math.pi)
    return nozzle_length

nozzle_length = length_nozzle(area_ratio, throat_area)

#determining the overall length of the motor
def total_length(nozzle_length, length_chamber):
    return nozzle_length + length_chamber

length_motor = total_length(nozzle_length, length_chamber)

#VALIDATION RELEVANT COMPUTATIONS

#figuring out the regression rate stuff
#asumptions (estimated based on literature)
a = 1       #coefficient of pressure. chosen from literature
n = 2       #pressure exponent. chosen from literature

#computing the regression rate based on literature chosen constants [mm/s]
#de Saint Robert's burning rate law
def regression_rate(chamber_pressure, pressure_coefficient, pressure_exponent):
    reg_rate = pressure_coefficient * chamber_pressure ** pressure_exponent
    return reg_rate

#computing the propellant burn area
def burn_area(regression_rate, mass_flow, rho):
    prop_burn_area = mass_flow / (regression_rate * rho)
    return prop_burn_area




# def do_stuff(rocket: Rocket):
#     """
#     :param rocket: Rocket class
#     :return: None
#     """
#     pass


# def run(rocket: Rocket) -> Rocket:
#     """
#     :param rocket: Original Rocket class
#     :return: Updated Rocket class
#     """

#     do_stuff(rocket)

#     return rocket


# if __name__ == "__main__":
#     test_rocket = Rocket()
#     run(test_rocket)



