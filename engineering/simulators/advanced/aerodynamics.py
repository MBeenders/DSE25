from numba import njit
import numpy as np

# Atmospheric layers with ceiling height and lapse rate
layers: np.ndarray = np.array([[0, -0.0065],  # ground
                               [11000, -0.0065],  # Troposphere
                               [20000, 0],  # Tropopause
                               [32000, 0.001],  # Stratosphere
                               [47000, 0.0028],  # Stratosphere
                               [51000, 0],  # Stratopause
                               [71000, -0.0028],  # Mesosphere
                               [86000, -0.0020],  # Mesosphere
                               [400000, 0],  # Assume constant from here
                               ])


@njit()
def isa(height: float) -> tuple[float, float, float]:
    g0 = 9.80665  # m/s^2
    R = 287.0  # J/kgK

    T0 = 288.15
    p0 = 101325
    T = T0
    p = p0

    if height > layers[-1][0]:
        return 0.0, 0.0, 0.0

    h = min(height, layers[-1][0])

    for i in range(1, len(layers)):  # Start in troposphere
        layer = layers[i]
        alpha = layer[1]
        delta_h = layer[0] - layers[i - 1][0]  # Full layer thickness
        if h <= layer[0]:
            # Final layer
            delta_h = h - layers[i - 1][0]

        last_T = T
        T += alpha * delta_h
        if alpha == 0:  # isothermal
            p *= np.exp(-g0 / (R * T) * delta_h)
        else:
            p *= (T / last_T) ** (-g0 / (alpha * R))

        if h <= layer[0]:
            break

    rho0 = p0 / (R * T0)

    rho = p / (R * T)

    return T, p, rho


# @njit()
# def drag(rocket, velocity: float, density: float, temperature: float) -> float:
#     """
#     :param rocket: Rocket Simulator class
#     :param velocity: [m/s]
#     :param density: [kg/m^3]
#     :param temperature: K
#     :param C_nc_0: Drag coefficient of the Nosecone (from literature) [-]
#     :return:
#     Barrowman presents methods for computing the drag of both fully turbulent
#     boundary layers and partially-laminar layers. Both methods were implemented
#     and tested, but the difference in apogee altitude was less than 5%
#     in with all tested designs. Therefore, the boundary layer is assumed to be
#     fully turbulent in all cases. (OpenRocket technical documentation, p. 43)
#     """
#
#     # Assume fully turbulent boundary layer
#
#     # SKIN FRICTION DRAG (C_f), applies to the wetted area of body and fins.
#     R_s = 0.5  # Surface roughness in micrometres
#     R_crit = 500000  # Critical reynolds number where transition occurs.
#     x = R_crit * 0.000015 / velocity  # Position of transition
#     C_fr = 0.032 * (R_s / x) ** 0.2  # Derived by Barrowman for fully turbulent flow, assuming a smooth surface.
#
#     # Taking into account compressibility and geometry effects
#     a = np.sqrt(1.4 * 287 * temperature)  # Speed of sound [m/s]
#     M = velocity / a  # Mach number [-]
#     q = 0.5 * density * velocity ** 2  # Dynamic pressure [Pa]
#
#     if M < 1:
#         C_fr_c = C_fr * (1 - 0.1 * M ** 2)
#         C_fr_c_l = C_fr * (1 + 0.18 * M ** 2) ** (-1)
#
#         if C_fr_c_l > C_fr_c:
#             C_fr_c = C_fr_c_l
#         else:
#             C_fr_c = C_fr_c
#
#     else:
#         C_fr_c = C_fr * (1 + 0.15 * M ** 2) ** (-0.58)
#         C_fr_c_l = C_fr * (1 + 0.18 * M ** 2) ** (-1)
#
#         if C_fr_c_l > C_fr_c:
#             C_fr_c = C_fr_c_l
#         else:
#             C_fr_c = C_fr_c
#
#     f_B = rocket.fineness_ratio  # Fineness ratio of the rocket ===== MAKE VARIABLE FORM
#     S_ref = rocket.wetted_area  # Wet surface area of entire rocket [m^2] ===== take from OpenRocket
#     S_w_b = rocket.wetted_area_body  # Wet surface area of body [m^2] ===== MAKE VARIABLE FORM from centrepressure.py
#     S_w_fin = rocket.wetted_area_fins  # Wet surface area of fins [m^2] ===== MAKE VARIABLE FORM from centrepressure.py
#     t_fin = rocket.fin_thickness  # Thickness of fins [m] ===== MAKE VARIABLE FORM or set a value
#     mac_fin = rocket.fin_mac  # Mean aerodynamic chord length of fins [m] ===== MAKE VARIABLE FORM
#     C_D_fr = C_fr_c * (((1 + (1 / (2 * f_B))) * S_w_b) + ((1 + (2 * t_fin / mac_fin)) * S_w_fin)) / S_ref
#     D_fr = C_D_fr * rocket.wetted_area * q  # Total frictional drag force of vehicle [N]
#
#     # NOSE CONE PRESSURE DRAG
#     # NOSECONE - 5:1 Haack (optimised for length and diameter, where c = 0; also optimised for wave and skin friction drag)
#
#     # 5:1 L-D Haack minimum drag noses
#     c = 0  # Optimisation coefficient        [-]
#     X = 0.024  # Axial distance from the nose [m]
#     L = 5 * rocket.diameter1  # Model length                  [m]
#     R = 0.075  # Model base radius            [m]
#
#     phi = np.arccos(1 - 2 * (X / L))  # [rad]
#     r = (R / np.sqrt(np.pi)) * np.sqrt(phi - 0.5 * np.sin(2 * phi) + c * np.sin(phi) ** 3)  # Model local radius [m]
#
#     f_N = 5  # Fineness ratio of nose
#     phi = rocket.joint_angle * np.pi / 180  # Nose cone joint angle [rad] ===== MAKE VARIABLE FORM
#     C_D_nc = 0.8 * np.sin(phi) ** 2  # Approximate nose pressure drag coefficient at M=0, phi<30 [deg]
#     b = 0.3  # ===== I HAVE NO IDEA WHAT THIS EMPIRICAL CONSTANT IS!!!
#     C_D_nc_s = rocket.C_nc_0 * (4 ** b) ** (np.log(f_N + 1) / np.log(4))  # Includes supersonic factor
#     C_D_nc = C_D_nc_s + C_D_nc  # Includes compressibility correction for sub and supersonic speeds
#     S_nc = np.pi * rocket.diameter1 * r  # Surface area of nose cone [m^2]
#     D_nc = C_D_nc * q * S_nc  # Nose cone pressure drag [N]
#
#     # SHOULDER PRESSURE DRAG (separation stage)
#     if M <= 1:
#         C_D_sh = C_D_nc
#     else:
#         C_D_sh = 0
#
#     L_t = 0.2  # Separation stage length [m]
#     theta = np.arcsin((rocket.diameter2 - rocket.diameter1) / (2 * L_t))
#     S_sh = np.pi * rocket.diameter2 * L_t * np.cos(theta)  # Shoulder wet surface area [m^2]
#     D_sh = C_D_sh * q * S_sh  # Shoulder pressure drag [N]
#
#     # FIN PRESSURE DRAG (Assume that flow is perpendicular to the leading edge)
#     # Assume for fins with tapering trailing edges, the base drag is zero.
#     if M <= 0.9:
#         C_D_LE = -1 + (1 - M ** 2) ** (-0.417)
#     elif 0.9 < M <= 1:
#         C_D_LE = 1 - 1.785 * (M - 0.9)
#     else:
#         C_D_LE = 1.214 - 0.502 / (M ** 2) + 0.1095 / (M ** 4)
#
#     G_LE = 45 * np.pi / 180  # Leading edge angle of slanted fin [rad]
#     C_D_LE = C_D_LE * np.cos(G_LE) ** 2  # Slanted fin cross-flow principle [-]
#     b = 0.225  # Fin span [m]
#     S_fin = t_fin * b / np.cos(G_LE)  # Surface area of fins that the flow sees [m^2]
#     D_fin = C_D_LE * q * S_fin  # Fin pressure drag [N]
#
#     # BASE DRAG
#     if M <= 1:
#         C_D_base = 0.12 + 0.13 * (M ** 2)
#     else:
#         C_D_base = 0.25 / M
#
#     t = 0.003  # Skin thickness [m]
#     S_base = np.pi * rocket.diameter2 * t  # Surface area of base (Diameter of lower stage * thickness * PI) [m^2]
#     D_base = C_D_base * q * S_base  # Base drag [N]
#
#     # TOTAL DRAG FORCE [N]
#     force_drag = D_base + 4 * D_fin + D_sh + D_nc + D_fr
#
#     return force_drag


@njit()
def skin_friction_drag(rocket, stage1: bool, stage2: bool, velocity: float, dynamic_pressure: float, mach_number: float) -> float:
    surface_roughness: float = 50E-6
    critical_reynolds: float = 500E3
    transition_position: float = (1.5E-5 * critical_reynolds) / velocity

    # Skin friction coefficient derived by Barrowman for fully turbulent flow, assuming a smooth surface
    c_friction: float = 0.032 * (surface_roughness / transition_position) ** 0.2

    # Check regime
    if mach_number < 1:
        c_friction_c = c_friction * (1 - 0.1 * mach_number ** 2)
        c_friction_c_l = c_friction * (1 + 0.18 * mach_number ** 2) ** (-1)

        if c_friction_c_l > c_friction_c:
            c_friction_c = c_friction_c_l
        else:
            c_friction_c = c_friction_c

    else:
        c_friction_c = c_friction * (1 + 0.15 * mach_number ** 2) ** (-0.58)
        c_friction_c_l = c_friction * (1 + 0.18 * mach_number ** 2) ** (-1)

        if c_friction_c_l > c_friction_c:
            c_friction_c = c_friction_c_l
        else:
            c_friction_c = c_friction_c

    # Calculate drag due to friction
    if stage1 and stage2:
        drag_coefficient_friction = c_friction_c * (((1 + (1 / (2 * rocket.fineness_ratio))) * rocket.wetted_area_body)
                                                    + ((1 + (2 * rocket.fin_thickness1 / rocket.fin_mac1)) * rocket.wetted_area_fins1)
                                                    + ((1 + (2 * rocket.fin_thickness2 / rocket.fin_mac2)) * rocket.wetted_area_fins2)) / rocket.reference_area
    elif stage1:
        drag_coefficient_friction = c_friction_c * (((1 + (1 / (2 * rocket.fineness_ratio))) * rocket.wetted_area_body)
                                                    + ((1 + (2 * rocket.fin_thickness1 / rocket.fin_mac1)) * rocket.wetted_area_fins1)) / rocket.reference_area
    elif stage2:
        drag_coefficient_friction = c_friction_c * (((1 + (1 / (2 * rocket.fineness_ratio))) * rocket.wetted_area_body)
                                                    + ((1 + (2 * rocket.fin_thickness2 / rocket.fin_mac2)) * rocket.wetted_area_fins2)) / rocket.reference_area
    else:
        drag_coefficient_friction = 0

    drag_friction = drag_coefficient_friction * rocket.reference_area * dynamic_pressure

    return drag_friction


@njit()
def nosecone_pressure_drag(rocket, dynamic_pressure: float, mach_number: float) -> tuple[float, float]:
    # 5:1 L-D Haack Nosecone
    if mach_number <= 1:
        reference_cd = 0
        stagnation_factor = 1 + (mach_number**2 / 4) + (mach_number**4 / 40)
    else:
        reference_cd = 0.1
        stagnation_factor = 1.84 - (0.76 / mach_number**2) + (0.166 / mach_number ** 4) + (0.035 / mach_number ** 6)

    # Blunt cylinder
    blunt_cd = 0.85 * stagnation_factor

    # Corrected pressure
    fineness_ratio = 5
    drag_coefficient_nosecone = blunt_cd * (reference_cd / blunt_cd) ** (np.log(fineness_ratio + 1) / np.log(4))

    frontal_area = np.pi * (rocket.diameter2 / 2)**2
    drag_nosecone = drag_coefficient_nosecone * dynamic_pressure * frontal_area

    # print("Nosecone: ", drag_coefficient_nosecone)
    return drag_nosecone, drag_coefficient_nosecone


@njit()
def shoulder_pressure_drag(rocket, drag_coefficient_nose: float, dynamic_pressure: float) -> float:
    shoulder_ref_area = np.pi / 4 * (rocket.diameter1 ** 2 - rocket.diameter2 ** 2)
    drag_shoulder = drag_coefficient_nose * dynamic_pressure * shoulder_ref_area  # Shoulder pressure drag [N]

    # print("Shoulder: ", drag_coefficient_shoulder)
    return drag_shoulder


@njit()
def fin_pressure_drag(rocket, stage1: bool, stage2: bool, dynamic_pressure: float, mach_number: float) -> (float, float):
    if mach_number <= 0.9:
        drag_coefficient_leading_edge = -1 + (1 - mach_number ** 2) ** (-0.417)
    elif 0.9 < mach_number <= 1:
        drag_coefficient_leading_edge = 1 - 1.785 * (mach_number - 0.9)
    else:
        drag_coefficient_leading_edge = 1.214 - 0.502 / (mach_number ** 2) + 0.1095 / (mach_number ** 4)

    leading_edge_angle = np.deg2rad(30)  # Make it a variable - Leading edge angle of slanted fin [rad]
    drag_coefficient_leading_edge = drag_coefficient_leading_edge * (np.cos(leading_edge_angle) ** 2)  # Slanted fin cross-flow principle [-]

    if stage1:
        fin_surface1 = rocket.fin_thickness1 * rocket.fin_span1 / np.cos(leading_edge_angle)  # Surface area of fins that the flow sees [m^2]
        drag_fin1 = drag_coefficient_leading_edge * dynamic_pressure * fin_surface1  # Fin pressure drag [N]
    else:
        drag_fin1 = 0

    if stage2:
        fin_surface2 = rocket.fin_thickness2 * rocket.fin_span2 / np.cos(leading_edge_angle)  # Surface area of fins that the flow sees [m^2]
        drag_fin2 = drag_coefficient_leading_edge * dynamic_pressure * fin_surface2  # Fin pressure drag [N]
    else:
        drag_fin2 = 0

    # print("Fins: ", drag_coefficient_leading_edge)
    return drag_fin1, drag_fin2


@njit()
def base_drag(rocket, dynamic_pressure: float, mach_number: float) -> float:
    if mach_number <= 1:
        drag_coefficient = 0.12 + 0.13 * (mach_number ** 2)
    else:
        drag_coefficient = 0.25 / mach_number

    t = 0.003  # Skin thickness [m]
    surface_area = np.pi * rocket.diameter2 * t  # Surface area of base (Diameter of lower stage * thickness * PI) [m^2]
    drag_base = drag_coefficient * dynamic_pressure * surface_area  # Base drag [N]

    # print("BaseDrag: ", drag_coefficient)
    return drag_base


@njit()
def drag(rocket, velocity: float, temperature: float, density: float, stage: int) -> float:
    if velocity > 0:
        # Taking into account compressibility and geometry effects
        speed_of_sound = np.sqrt(1.4 * 287 * temperature)  # [m/s]
        mach_number = velocity / speed_of_sound  # [-]
        dynamic_pressure = 0.5 * density * velocity ** 2  # [Pa]


        # Calculate drag forces
        drag_nosecone, drag_coefficient_nose = nosecone_pressure_drag(rocket, dynamic_pressure, mach_number)
        drag_base = base_drag(rocket, dynamic_pressure, mach_number)

        if stage == 0:  # Total Stage
            drag_shoulder = shoulder_pressure_drag(rocket, drag_coefficient_nose, dynamic_pressure)
            drag_friction = skin_friction_drag(rocket, True, True, velocity, dynamic_pressure, mach_number)
            drag_fin1, drag_fin2 = fin_pressure_drag(rocket, True, True, dynamic_pressure, mach_number)
            drag_force = drag_friction + drag_nosecone + drag_shoulder + drag_fin1 + drag_fin2 + drag_base
            # print(f"Shoulder {drag_shoulder}\nNosecone {drag_nosecone}\nBase {drag_base}\nFriction {drag_friction}\nFin1 {drag_fin1}\nFin2 {drag_fin2}\nTotal {drag_force}")
        elif stage == 1:  # Stage 1
            drag_shoulder = shoulder_pressure_drag(rocket, drag_coefficient_nose, dynamic_pressure)
            drag_friction = skin_friction_drag(rocket, True, False, velocity, dynamic_pressure, mach_number)
            drag_fin1, drag_fin2 = fin_pressure_drag(rocket, True, False, dynamic_pressure, mach_number)
            drag_force = drag_friction + drag_shoulder + drag_fin1 + drag_base
            # print(f"Shoulder {drag_shoulder}\nNosecone {drag_nosecone}\nBase {drag_base}\nFriction {drag_friction}\nFin1 {drag_fin1}\nFin2 {drag_fin2}\nTotal {drag_force}")
        else:  # Stage 2
            drag_friction = skin_friction_drag(rocket, False, True, velocity, dynamic_pressure, mach_number)
            drag_fin1, drag_fin2 = fin_pressure_drag(rocket, False, True, dynamic_pressure, mach_number)
            drag_force = drag_friction + drag_nosecone + drag_fin2 + drag_base
            # print(f"\nNosecone {drag_nosecone}\nBase {drag_base}\nFriction {drag_friction}\nFin1 {drag_fin1}\nFin2 {drag_fin2}\nTotal {drag_force}")

    else:
        drag_force = 0

    return drag_force


if __name__ == "__main__":
    pass
