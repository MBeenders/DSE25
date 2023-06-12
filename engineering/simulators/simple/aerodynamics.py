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
def isa(height: float) -> tuple:
    g0 = 9.80665  # m/s^2
    R = 287.0  # J/kgK

    T0 = 288.15
    p0 = 101325
    T = T0
    p = p0

    if height > layers[-1][0]:
        return 0, 0, 0

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


@njit()
def drag(rocket, velocity: np.ndarray, density: float) -> np.ndarray:
    """
    :param rocket: Rocket class
    :param velocity: [m/s]
    :param density: [kg/m^3]
    :return: Drag force [N]
    """
    area = np.pi * (rocket.diameter / 2) ** 2

    return (0.5 * density * velocity ** 2) * area * rocket.cd  # Force


if __name__ == "__main__":
    # Density vs altitude example
    hs = np.linspace(0, 200000, 100)
    rhos = []
    for h in hs:
        rhos.append(isa(h)[2])

    import matplotlib.pyplot as plt

    plt.plot(rhos, hs)
    plt.show()
