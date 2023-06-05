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
        self.new_rocket: Rocket = Rocket()

        # Import the run parameters
        self.run_parameters_file = open("files/run_parameters.json")
        self.run_parameters: dict = json.load(self.run_parameters_file)
        self.selection: list[str] = self.run_parameters["sizing_selection"]

    def give_id(self, subsystem):
        serial_num = int(subsystem.id.split(".")[1])
        serial_num += 1
        subsystem.id = f"{self.rocket.id}.{serial_num}"

    def run_sizing(self):
        sized_dict: dict = {}  # Dictionary with all sized classes
        if "engine_1" in self.selection:
            sized_dict["engine_1"] = run_engine_sizing(copy.deepcopy(self.rocket))["engine_1"]
        if "engine_2" in self.selection:
            sized_dict["engine_2"] = run_engine_sizing(copy.deepcopy(self.rocket))["engine_2"]
        if "recovery_1" in self.selection:
            sized_dict["recovery_1"] = run_recovery_sizing(copy.deepcopy(self.rocket))["recovery_1"]
        if "recovery_2" in self.selection:
            sized_dict["recovery_2"] = run_recovery_sizing(copy.deepcopy(self.rocket))["recovery_2"]
        if "structure" in self.selection:
            sized_dict["structure"] = run_structure_sizing(copy.deepcopy(self.rocket))["structure"]

        for key, item in sized_dict.items():
            self.give_id(item)
            self.new_rocket[key] = item

    def close(self):
        self.run_parameters_file.close()


if __name__ == "__main__":
    runner = Runner("initial_values")
    runner.run_sizing()
    runner.close()
