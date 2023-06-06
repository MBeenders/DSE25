from engineering.sizing.rocket import Rocket

#Constant values:
g = 9.80665



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
    #print(rocket.stage1.recovery.descent_rate)

    return rocket


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
