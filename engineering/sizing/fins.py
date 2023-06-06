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
    # a = M / v # speed of sound [m/s]
    t = 0.005  # wing thickness [m]
    c_r = 0.4  # root chord length [m]
    c_t = 0.1  # tip chord length [m]
    b = 0.3  # semi-span length [m]
    p = 12000  # air pressure [Pa]
    S = 0.5 * b * (c_t + c_r)  # surface area [m^2]
    AR = (b ** 2) / S  # aspect ratio [-]
    TR = c_t / c_r  # taper ratio [-]
    finnumberlower = 4  # Number of fins on the lower stage
    finnumberupper = 4  # Number of fins on the upper stage

    v_f = np.sqrt(G / ((1.337 * p * (1 + TR) * AR ** 3) / (2 * (AR + 2) * (t / c_r) ** 3)))  # fin flutter speed [m/s]
    print(v_f)

    # Fin thickness

    sweep_LE = 30 * np.pi / 180  # sweep angle of leading edge [rad]
    A = t * (b / np.cos(sweep_LE))  # area experienced by airflow [m^2]
    C_D_f = 0.12  # fin drag coefficient [-]
    v = 200  # velocity [m/s]

    F_d = 0.5 * p * v ** 2 * C_D_f * A  # drag force [N]
    print(F_d)

    fincantlower = np.deg2rad(5)  # Cant of the lower stage fins [rad]
    fincantupper = 0  # Cant of the upper stage fins [rad]
    rotrate = 0
    centroidlower = rocket.stage1.diameter/2 + ((c_r +2*c_t)/(3*(c_r+c_t))*b)

    #Lower stage
    if t < t_separation:
        AOA_fin_lower = fincantlower - np.arctan(centroidlower*rotrate/v) # Effective angle of attack of the centroid of the fin
        clift1fin = 2 * np.pi * AOA_fin_lower #Coeffient of lift of a flat plate
        cdrag1fin = #Coefficient of drag of a flat plate
        lift1fin = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * S * clift1fin
        drag1fin = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * S * cdrag1fin
        moment1fin = (np.cos(centroidlower*rotrate/v)*lift1fin - drag1fin*np.sin(centroidlower*rotrate/v)) * centroidlower #Moment averaged at centroid
        momentlower = moment1fin*finnumberlower #Multiple fins
    else:
        momentlower = 0

    #Upper stage
    AOA_fin_upper = fincantupper - np.arctan(centroidupper*rotrate/v)
    clift1finu = 2 * np.pi * AOA_fin_upper
    cdrag1finu =
    lift1finu = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * S * clift1finu
    drag1finu = 0.5 * rho * (v**2 + (rotrate*centroidlower)**2) * S * cdrag1finu
    moment1finu = (np.cos(centroidupper*rotrate/v)*lift1finu - drag1finu*np.sin(centroidupper*rotrate/v)) * centroidupper
    momentupper = moment1finu *finnumberupper

    angacc = (momentlower + momentupper)/MMOI #Angular acceleration, MMOI should depend on time, as fuel is burned and staging occurs
    rotrate += angacc * dt #Rate of rotation is updated




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
