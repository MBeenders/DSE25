from numba import njit
import numpy as np


@njit()
def density(height):
    # TODO add ISA
    return 1.225


@njit()
def drag(velocity: np.ndarray, height: float) -> np.ndarray:
    """
    :param velocity:
    :param height:
    :return:
    """
    drag_coefficient: float = 0.5  # -
    radius: float = 0.3  # m
    frontal_area: float = np.pi * radius**2  # m^2

    return drag_coefficient * frontal_area * 0.5 * density(height) * velocity**2
