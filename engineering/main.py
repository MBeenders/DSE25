from sizing.rocket import Rocket
from sizing.engine import run as run_engine_sizing
from sizing.recovery import run as run_recovery_sizing
from file_manager import initialize_rocket


class Runner:
    def __init__(self, file_name: str):
        """
        :param file_name: Name of the rocket initialization file
        """
        self.rocket: Rocket = initialize_rocket(file_name)

    def run_sizing(self, selection: list[str]):
        """
        :param selection:
        """
        if "engine" in selection:
            run_engine_sizing(self.rocket)
        if "recovery" in selection:
            run_recovery_sizing(self.rocket)


if __name__ == "__main__":
    runner = Runner("initial_values")
