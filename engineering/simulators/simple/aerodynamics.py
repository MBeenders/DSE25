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
    C_fr = 0.032 * (R_s/x)**0.2 # Derived by Barrowman for fully turbulent flow, assuming a smooth surface.

    # Taking into account compressibility and geometry effects
    a = np.sqrt(1.4*287*temp(height)) # Speed of sound [m/s]
    M = velocity/a # Mach number [-]
    q = 0.5 * density(height) * velocity ** 2 # Dynamic pressure [Pa]

    if M < 1:
        C_fr_c = C_fr * (1-0.1*M**2)
        C_fr_c_l = C_fr * (1+0.18*M**2)**(-1)

        if C_fr_c_l>C_fr_c:
            C_fr_c = C_fr_c_l
        else:
            C_fr_c = C_fr_c

    elif M >= 1:
        C_fr_c = C_fr * (1+0.15*M**2)**(-0.58)
        C_fr_c_l = C_fr * (1 + 0.18 * M ** 2) ** (-1)

        if C_fr_c_l > C_fr_c:
            C_fr_c = C_fr_c_l
        else:
            C_fr_c = C_fr_c

    # BODY PRESSURE DRAG (apply for both stages)
    f_B = 15 # Fineness ratio of the rocket ===== MAKE VARIABLE FORM
    S_w_b = 4000 # Wet surface area of body [m^2] ===== MAKE VARIABLE FORM
    S_w_fin = 20 # Wet surface area of body [m^2] ===== MAKE VARIABLE FORM
    t_fin = 0.005 # Thickness of fins [m] ===== MAKE VARIABLE FORM
    mac_fin = 0.5 # Mean aerodynamic chord length of fins [m] ===== MAKE VARIABLE FORM
    C_D_f = C_fr_c * (((1+(1/(2*f_B)))*S_w_b) + ((1+(2*t_fin/mac_fin))*S_w_fin))/(S_ref)
    D_f = C_D_f * S_w * q # Total frictional drag force of vehicle [N]

    # NOSE CONE PRESSURE DRAG
    # NOSECONE - 5:1 Haack (optimised for length and diameter, where c = 0; also optimised for wave and skin friction drag)

    # 5:1 L-D Haack minimum drag noses
    c = 0  # Optimisation coefficient        [-]
    X = 0.024  # Axial distance from the nose [m]
    L = 5 * D_u  # Model length                  [m]
    R = 0.075  # Model base radius            [m]

    phi = np.arccos(1 - 2 * (X / L))  # [rad]
    r = (R / np.sqrt(np.pi)) * np.sqrt(phi - 0.5 * np.sin(2 * phi) + c * np.sin(phi) ** 3)  # Model local radius [m]

    f_N = 5 # Fineness ratio of nose
    phi = 22 * np.pi/180 # Nose cone joint angle [rad] ===== MAKE VARIABLE FORM
    C_D_nc = 0.8 * np.sin(phi)**2 # Approximate nose pressure drag coefficient at M=0, phi<30 [deg]
    b = 0.3 # ===== I HAVE NO IDEA WHAT THIS EMPIRICAL CONSTANT IS!!!
    C_D_nc_s = C_nc_0 * (4**b) ** (np.log(f_N + 1)/np.log(4)) # Includes supersonic factor
    C_D_nc = C_D_nc_s + C_D_nc # Includes compressibility correction for sub and supersonic speeds
    S_nc = np.pi * D_u * r # Surface area of nose cone [m^2]
    D_nc = C_D_nc * q * S_nc # Nose cone pressure drag [N]

    # SHOULDER PRESSURE DRAG (separation stage)
    if M <=1:
        C_D_sh = C_D_nc
    else:
        C_D_sh = 0

    L_t = 0.2 # Separation stage length [m]
    theta = np.arcsin((D_l-D_u)/(2*L_t))
    S_sh = np.pi * D_l * L_t*np.cos(theta) # Shoulder wet surface area [m^2]
    D_sh = C_D_sh * q * S_sh # Shoulder pressure drag [N]

    # FIN PRESSURE DRAG (Assume that flow is perpendicular to the leading edge)
    # Assume for fins with tapering trailing edges, the base drag is zero.
    if M <= 0.9:
        C_D_LE = -1 + (1-M**2)**(-0.417)
    elif 0.9 < M <= 1:
        C_D_LE = 1 - 1.785 * (M-0.9)
    elif M > 1:
        C_D_LE = 1.214 - 0.502/(M**2) + 0.1095/(M**4)

    G_LE = 45 * np.pi/180 # Leading edge angle of slanted fin [rad]
    C_D_LE = C_D_LE * np.cos(G_LE)**2 # Slanted fin cross-flow principle [-]
    b = 0.225 # Fin span [m]
    S_fin = t_fin * b / np.cos(G_LE) # Surface area of fins that the flow sees [m^2]
    D_fin = C_D_LE * q * S_fin # Fin pressure drag [N]

    # BASE DRAG
    if M <= 1:
        C_D_base = 0.12 + 0.13 * (M**2)
    if M > 1:
        C_D_base = 0.25/M

    t = 0.003 # Skin thickness [m]
    S_base = np.pi * D_l * t # Surface area of base (Diameter of lower stage * thickness * PI) [m^2]
    D_base = C_D_base * q * S_base # Base drag [N]

    # TOTAL DRAG FORCE [N]
    force_drag = D_base + 4*D_fin + D_sh + D_nc + D_f + D_fr

    return force_drag


if __name__ == "__main__":
    # Density vs altitude example
    hs = np.linspace(0, 200000, 100)
    rhos = []
    for h in hs:
        rhos.append(density(h))

    import matplotlib.pyplot as plt
    plt.plot(rhos, hs)
    plt.show()
