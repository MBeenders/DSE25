from rocket import Rocket


def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    rocket.mass = 5


def run(rocket: Rocket):
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    print(f"Mass before functions: {rocket.mass}")
    do_stuff(rocket)
    print(f"Mass after functions: {rocket.mass}")

    pass


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
