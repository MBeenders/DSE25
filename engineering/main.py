import copy
import json

from sizing.rocket import Rocket
from sizing.engine import run as run_engine_sizing
from sizing.recovery import run as run_recovery_sizing
from sizing.structure import run as run_structure_sizing
from file_manager import initialize_rocket


class Runner:
    def __init__(self, file_name: str):
        """
        :param file_name: Name of the rocket initialization file
        """
        self.rocket: Rocket = initialize_rocket(file_name)

        # Import the run parameters
        self.run_parameters_file = open("files/run_parameters.json")
        self.run_parameters: dict = json.load(self.run_parameters_file)
        self.selection: list[str] = self.run_parameters["sizing_selection"]

    def run_sizing(self):
        if "engine" in self.selection:
            run_engine_sizing(copy.deepcopy(self.rocket))
        if "recovery" in self.selection:
            run_recovery_sizing(copy.deepcopy(self.rocket))
        if "structure" in self.selection:
            run_structure_sizing(copy.deepcopy(self.rocket))

    def close(self):
        self.run_parameters_file.close()


if __name__ == "__main__":
    runner = Runner("initial_values")
    runner.close()
