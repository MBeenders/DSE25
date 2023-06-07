from numba import njit
import numpy as np


# Atmospheric layers with ceiling height and lapse rate
layers: np.ndarray = np.array([[0, -0.0065], # ground
                              [11000, -0.0065], # Troposphere
                              [20000, 0], # Tropopause
                              [32000, 0.001], # Stratosphere
                              [47000, 0.0028], # Stratosphere
                              [51000, 0], # Stratopause
                              [71000, -0.0028], # Mesosphere
                              [86000, -0.0020], # Mesosphere
                              [400000, 0], # Assume constant from here
                              ]) 

@njit()
def density(height: float) -> float:

    g0 = 9.80665 # m/s^2
    R = 287.0 # J/kgK

    T0 = 288.15
    p0 = 101325
    T = T0
    p = p0

    if height > layers[-1][0]:
        return 0.0

    h = min(height, layers[-1][0])

    for i in range(1, len(layers)): # Start in troposphere
        layer = layers[i]
        alpha = layer[1]
        delta_h = layer[0] - layers[i-1][0] # Full layer thickness
        if h <= layer[0]:
            # Final layer
            delta_h = h - layers[i-1][0]

        last_T = T
        T += alpha * delta_h
        if alpha == 0: # isothermal
            p *= np.exp(-g0/(R*T) * delta_h)
        else:
            p *= (T/last_T)**(-g0/(alpha * R))

        if h <= layer[0]:
            break

    rho0 = p0/(R*T0)

    rho = p/(R*T)
    
    return rho


@njit()
def drag(velocity: np.ndarray, height: float) -> np.ndarray:
    """
    :param velocity:
    :param height:
    :return:
    #Barrowman presents methods for computing the drag of both fully turbulent
    boundary layers and partially-laminar layers. Both methods were implemented
    and tested, but the difference in apogee altitude was less than 5%
    in with all tested designs. Therefore, the boundary layer is assumed to be
    fully turbulent in all cases. (OpenRocket technical documentation, p. 43)
    """
    # Assume fully turbulent boundary layer

    # SKIN FRICTION DRAG (C_f), applies to the wetted area of body and fins.
    R_s = 0.5 # Surface roughness in micrometres
    R_crit = 500000 # Critical reynolds number where transition occurs.
    x = R_crit * 0.000015 / velocity # Position of transition
    S_w = 0 # Total wetted surface area of body and fins
    C_f = 0.032 * (R_s/x)**0.2 # Derived by Barrowman for fully turbulent flow, assuming a smooth surface.

    # Taking into account compressibility and geometry effects
    a = np.sqrt(1.4*287*temp(height))
    M = velocity/a

    if M < 1:
        C_f_c = C_f * (1-0.1*M**2)
        C_f_c_l = C_f * (1+0.18*M**2)**(-1)

        if C_f_c_l>C_f_c:
            C_f_c = C_f_c_l
        else:
            C_f_c = C_f_c

    elif M >= 1:
        C_f_c = C_f * (1+0.15*M**2)**(-0.58)
        C_f_c_l = C_f * (1 + 0.18 * M ** 2) ** (-1)

        if C_f_c_l > C_f_c:
            C_f_c = C_f_c_l
        else:
            C_f_c = C_f_c

    # The body wetted area is corrected for its cylindrical geometry, and the fins for their finite thickness.
    f_B = 15 # Fineness ratio of the rocket ===== MAKE VARIABLE FORM
    S_w_b = 4000 # Wet surface area of body [m^2] ===== MAKE VARIABLE FORM
    S_w_fin = 20 # Wet surface area of body [m^2] ===== MAKE VARIABLE FORM
    t_fin = 0.005 # Thickness of fins [m] ===== MAKE VARIABLE FORM
    mac_fin = 0.5 # Mean aerodynamic chord length of fins [m] ===== MAKE VARIABLE FORM
    C_D_f = C_f_c * (((1+(1/(2*f_B)))*S_w_b) + ((1+(2*t_fin/mac_fin))*S_w_fin))/(S_ref)
    D_f = C_D_f * (0.5 * S_w * density(height) * velocity ** 2)  # Total frictional drag force of vehicle [N]

    # BODY PRESSURE DRAG
    

    drag_coefficient: float = 0.5  # -
    radius: float = 0.3  # m
    frontal_area: float = np.pi * radius**2  # m^2
    force_drag = drag_coefficient * frontal_area * 0.5 * density(height) * velocity**2

    return force_drag


if __name__ == "__main__":
    # Density vs altitude example
    hs = np.linspace(0,200000, 100)
    rhos = []
    for h in hs:
        rhos.append(density(h))

    import matplotlib.pyplot as plt
    plt.plot(rhos, hs)
    plt.show()