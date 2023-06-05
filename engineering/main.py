from sizing.rocket import Rocket
import sizing.engine
from file_manager import initialize_rocket


class Runner:
    def __init__(self, file_name: str):
        """
        :param file_name: Name of the rocket initialization file
        """
        self.rocket: Rocket = initialize_rocket(file_name)


if __name__ == "__main__":
    runner = Runner("initial_values")
