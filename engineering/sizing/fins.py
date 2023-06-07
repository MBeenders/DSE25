import numpy as np
from engineering.sizing.rocket import Rocket


def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """

    # Fin sizing (variables: size, shape, sweep, number) (https://rocketry.gitbook.io/public/tutorials/airframe/sizing-fins)

    # Fin flutter
    # Maximum fin flutter must lie above the maximum rocket speed

    G = 26900000000  # shear modulus [Pa]
    a = 220 # speed of sound [m/s]
    t = 0.005  # wing thickness [m]
    c_rl = 0.4  # root chord length [m]
    c_tl = 0.1  # tip chord length [m]
    bl = 0.3  # semi-span length [m]
    p = 12000  # air pressure [Pa]
    Sl = 0.5 * bl * (c_tl + c_rl)  # surface area [m^2]
    ARl = (bl ** 2) / Sl  # aspect ratio [-]
    TRl = c_tl / c_rl  # taper ratio [-]
    c_ru = 0.2
    c_tu = 0.05
    bu = 0.015
    Su = 0.5 * bu * (c_tu + c_ru)
    ARu = (bu ** 2) / Su
    TRu = c_tu / c_ru
    finnumberlower = 4  # Number of fins on the lower stage
    finnumberupper = 4  # Number of fins on the upper stage

    v_f = a * np.sqrt(G / ((1.337 * p * (1 + TRl) * ARl ** 3) / (2 * (ARl + 2) * (t / c_rl) ** 3)))  # fin flutter speed [m/s]
    print(v_f)

    # Fin thickness

    sweep_LE = 30 * np.pi / 180  # sweep angle of leading edge [rad]
    Al = t * (bl / np.cos(sweep_LE))  # area experienced by airflow [m^2]
    C_D_f = 0.12  # fin drag coefficient [-]
    v = 200  # velocity [m/s]

    F_d = 0.5 * p * v ** 2 * C_D_f * Al  # drag force [N]
    print(F_d)

    fincantlower = np.deg2rad(5)  # Cant of the lower stage fins [rad]
    fincantupper = 0  # Cant of the upper stage fins [rad]
    rotrate = 0
    rotratelist = [0]
    centroidlower = rocket.stage1.diameter/2 + ((c_rl +2*c_tl)/(3*(c_rl+c_tl))*bl)
    centroidupper = rocket.stage2.diameter/2 + ((c_ru +2*c_tu)/(3*(c_ru+c_tu))*bu)

    #Lower stage
    if t < t_separation:
        AOA_fin_lower = fincantlower - np.arctan(centroidlower*rotrate/v) # Effective angle of attack of the centroid of the fin
        mu = 1.458 * 10**(-6) * Temp_air**(1.5) / (Temp_air + 110.4) # Kinematic viscosity of the air
        Reynoldslower = rho * (v**2 + (rotrate*centroidlower)**2) * (c_tl+c_rl)/(2*mu) #Reynolds number
        clift1fin = 2 * np.pi * AOA_fin_lower #Coeffient of lift of a flat plate
        cdrag1fin = 1.328/np.sqrt(Reynoldslower) #Coefficient of drag of a flat plate
        lift1fin = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * Sl * clift1fin
        drag1fin = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * Sl * cdrag1fin
        moment1fin = (np.cos(centroidlower*rotrate/v)*lift1fin - drag1fin*np.sin(centroidlower*rotrate/v)) * centroidlower #Moment averaged at centroid
        momentlower = moment1fin*finnumberlower #Multiple fins
    else:
        momentlower = 0

    #Upper stage
    AOA_fin_upper = fincantupper - np.arctan(centroidupper*rotrate/v)
    mu = 1.458 * 10 ** (-6) * Temp_air ** (1.5) / (Temp_air + 110.4)  # Kinematic viscosity of the air
    Reynoldsupper = rho * (v ** 2 + (rotrate * centroidupper) ** 2) * (c_tu + c_ru) / (2 * mu)  # Reynolds number at half fin
    clift1finu = 2 * np.pi * AOA_fin_upper
    cdrag1finu = 1.328/np.sqrt(Reynoldsupper)
    lift1finu = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * Su * clift1finu
    drag1finu = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * Su * cdrag1finu
    moment1finu = (np.cos(centroidupper*rotrate/v)*lift1finu - drag1finu*np.sin(centroidupper*rotrate/v)) * centroidupper
    momentupper = moment1finu *finnumberupper

    angacc = (momentlower + momentupper)/MMOI #Angular acceleration, MMOI should depend on time, as fuel is burned and staging occurs
    rotrate += angacc * dt #Rate of rotation is updated
    rotratelist += [rotrate]



def run(rocket: Rocket) -> Rocket:
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    do_stuff(rocket)

    return rocket


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
