import numpy as np

# NASA TN D-708

def size_yoyo_mass(rocket, wraps = 2):
    # assume that targeted rotation rate is 0.
    vehicle_inertia = rocket.stage2.mmoi # not yet implemented
    l = np.pi()*rocket.stage2.diameter
    stringweight = 2 * 980 * l * np.pi() * 1E-3**2 #density of dyneema is 980kg/m^3, multiply this by line volume
    m = vehicle_inertia/((l+diameter/2)**2)
    return m-1/3*stringweight

def yoyo_mmoi_contribution(rocket, mass):
    # Mass of both yoyo despin weights
    return mass*(rocket.stage2.diameter/2)**2