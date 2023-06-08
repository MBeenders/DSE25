import sys
import os

path = os.path.split(sys.argv[0])[0]
sys.path.append(path)

from sizing.rocket import Rocket
import numpy as np


def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    pass


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
