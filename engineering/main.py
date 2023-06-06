import copy
import json

from sizing.rocket import Rocket
from sizing.engine import run as run_engine_sizing
from sizing.recovery import run as run_recovery_sizing
from sizing.structure import run as run_structure_sizing
import file_manager as fm


class Runner:
    def __init__(self, file_name: str, run_id: int):
        """
        :param file_name: Name of the rocket initialization file
        :param run_id: ID of the current run
        """
        self.run_id = run_id

        if file_name[:7] == "archive":  # If name starts with archive, import the class from the archive
            self.rocket: Rocket = fm.import_rocket_iteration(file_name)
        else:  # If not, than just create a new class from the initialization file
            self.rocket: Rocket = fm.initialize_rocket(file_name)

        self.new_rocket: Rocket = Rocket()

        # Import the run parameters
        self.run_parameters_file = open("files/run_parameters.json")
        self.run_parameters: dict = json.load(self.run_parameters_file)
        self.selection: list[str] = self.run_parameters["sizing_selection"]

        # Import requirements
        self.requirements = fm.import_csv("requirements")

    def give_id(self, subsystem):
        serial_num = int(subsystem.id.split(".")[1])
        serial_num += 1
        subsystem.id = f"{self.rocket.id}.{serial_num}"

    def run_sizing(self):
        sized_dict: dict = {"stage1": {}, "stage2": {}}  # Dictionary with all sized classes
        if "stage1_engine" in self.selection:
            sized_dict["stage1"]["engine"] = run_engine_sizing(copy.deepcopy(self.rocket))["stage1"]["engine"]
        if "stage2_engine" in self.selection:
            sized_dict["stage2"]["engine"] = run_engine_sizing(copy.deepcopy(self.rocket))["stage2"]["engine"]
        if "stage1_recovery" in self.selection:
            sized_dict["stage1"]["recovery"] = run_recovery_sizing(copy.deepcopy(self.rocket))["stage1"]["recovery"]
        if "stage2_recovery" in self.selection:
            sized_dict["stage2"]["recovery"] = run_recovery_sizing(copy.deepcopy(self.rocket))["stage2"]["recovery"]
        if "stage1_structure" in self.selection:
            sized_dict["stage1"]["structure"] = run_structure_sizing(copy.deepcopy(self.rocket))["stage1"]["structure"]

        for stage_name, stage_classes in sized_dict.items():
            for subsystem_name, subsystem_data in stage_classes.items():
                self.give_id(subsystem_data)
                self.new_rocket[stage_name][subsystem_name] = subsystem_data

        # Increase Rocket ID by 1
        serial_num = int(self.rocket.id)
        serial_num += 1
        self.new_rocket.id = serial_num

    def check_compliance(self):
        for index, row in self.requirements.iterrows():
            print(row["Variable"])

    def save_iteration(self):
        fm.export_rocket_iteration("rocket", self.new_rocket, self.run_id)

    def export_to_catia(self):
        fm.export_catia_parameters("catia", self.new_rocket, self.run_parameters["catia_variables"])

    def close(self):
        self.run_parameters_file.close()


if __name__ == "__main__":
    runner = Runner("initial_values", 0)
    runner.run_sizing()
    runner.check_compliance()
    runner.close()
