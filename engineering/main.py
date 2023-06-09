import copy
import json
import os
import sys
import re

import numpy as np
import time

import file_manager as fm
from simulators.advanced.aerodynamics import drag, isa
from simulators.simple.dynamics import run as dynamics_run
from simulators.simple.gravity import gravity
from simulators.simulator import Simulator

from sizing.engine import run as run_engine_sizing, initialize_engines
from sizing.recovery import run as run_recovery_sizing
from sizing.structure import run as run_structure_sizing
from sizing.electronics import run as run_electronics_sizing
from sizing.rocket import Rocket


def extract_number(file):
    s = re.findall("\d+$",file)
    return int(s[0]) if s else 0, file


class Runner:
    def __init__(self, file_name: str):
        """
        :param file_name: Name of the rocket initialization file
        """
        self.current_file_path = os.path.split(sys.argv[0])[0]
        self.run_id: int = 0
        self.iteration_id: int = 0
        self.start_time: float = 0

        self.warnings: int = 0

        # Import the run parameters
        self.run_parameters_file = open(f"{self.current_file_path}/files/run_parameters.json")
        self.run_parameters: dict = json.load(self.run_parameters_file)
        self.selection: list[str] = self.run_parameters["sizing_selection"]

        simulator: Simulator = Simulator(self.run_parameters["mission_profile"], dynamics_run, gravity, drag, isa)
        if file_name[:7] == "archive":  # If name starts with archive, import the class from the archive
            self.rocket: Rocket = fm.import_rocket_iteration(file_name)
        else:  # If not, then just create a new class from the initialization file
            self.rocket: Rocket = fm.initialize_rocket(file_name, simulator, self.run_parameters)

        # Calculate all the Engine specs
        self.rocket = initialize_engines(self.rocket)

        self.new_rocket: Rocket = copy.deepcopy(self.rocket)

        # Import requirements
        self.requirements = fm.import_csv("requirements")

    def create_run_id(self, testing):
        save_directory = f"{self.current_file_path}/files/archive"
        # Make run_id based on last file created
        if os.listdir(save_directory) and not testing:
            self.run_id: int = int(max(os.listdir(f"{self.current_file_path}/files/archive"), key=extract_number).split("_")[1]) + 1
        else:
            self.run_id: int = 1

        # Check if file exists
        if not os.path.exists(f"{save_directory}/run_{self.run_id}"):
            os.makedirs(f"{save_directory}/run_{self.run_id}")

    def run(self, runs, save=True, print_iteration=True, print_sub=True, testing=False):
        print("Running Main Program")
        self.start_time = time.time()

        # Create an ID number to represent this run
        self.create_run_id(testing)

        # Check Rocket for missing parameters
        self.check_rocket_class()

        for i in range(runs):
            self.iteration_id = i
            last_time = time.time()

            if print_iteration:
                print(f"Iteration {i + 1}/{runs}")

            # Make sure all Subsystem parameters are summed into the Stages and main Rocket
            if print_sub:
                print("\tSumming Rocket Parameters")
            self.rocket.update()

            # Simulation
            if print_sub:
                print("\tPopulating Simulation (Temp solution!)")
            self.populate_simulation()
            if print_sub:
                print("\tRunning Simulation")
            self.rocket.simulator.run()
            self.rocket.simulator.plot_trajectory()
            if print_sub:
                print(f"\t\tInitial apogee: {self.rocket.simulator.apogee} m")

            # Sizing
            self.run_sizing(print_sub)

            # Sum the Subsystems into the Stages and main Rocket
            if print_sub:
                print("\tSumming Rocket Parameters")
            self.new_rocket.update()

            # Save iteration
            if save:
                if print_sub:
                    print("\tSaving Iteration")
                if testing:
                    fm.export_rocket_iteration(f"run_1/{self.iteration_id}", self.new_rocket)
                else:
                    fm.export_rocket_iteration(f"run_{self.run_id}/{self.iteration_id}_rocket", self.new_rocket)

            # Overwrite old Rocket with New Rocket
            self.rocket = self.new_rocket

            if print_iteration:
                print(f"Finished iteration {i + 1}, after {round(time.time() - last_time, 2)} s")

        # Close
        print(f"Finished after {round(time.time() - self.start_time, 2)} s\n\tClosing program ...")
        self.close()

    def give_id(self, subsystem):
        serial_num = int(subsystem.id.split(".")[1])
        serial_num += 1
        subsystem.id = f"{self.rocket.id}.{serial_num}"

    def populate_simulation(self):
        # Temp
        self.rocket.stage1.engine.thrust_curve = 1000 * np.ones(100)
        self.rocket.stage2.engine.thrust_curve = 1000 * np.ones(100)
        self.rocket.stage1.engine.fuel_mass = np.linspace(10, 0, 100)
        self.rocket.stage2.engine.fuel_mass = np.linspace(10, 0, 100)
        # print(self.rocket.stage1.engine.thrust_curve)
        self.rocket.simulator.create_stages(self.rocket)

    def run_sizing(self, print_status=True):
        if print_status:
            print("\tRunning Sizing")

        flight_data = self.rocket.simulator.stages  # Flight data from the different stages
        self.rocket.simulator.delete_stages()

        def sizer(subsystem, function, separate=False):
            if print_status:
                print(f"\t\tSizing {subsystem.capitalize()}")

            rocket = copy.deepcopy(self.rocket)
            rocket.simulator.stages = flight_data

            if separate:
                try:
                    sized_dict["stage1"][subsystem] = function(rocket, "stage1")["stage1"][subsystem]
                    sized_dict["stage2"][subsystem] = function(rocket, "stage2")["stage2"][subsystem]
                except Exception as error:
                    print(f"\t\t!! {subsystem.capitalize()} sizing failed with: {error}")
            else:
                try:
                    sizing = function(rocket)
                    sized_dict["stage1"][subsystem] = sizing["stage1"][subsystem]
                    sized_dict["stage2"][subsystem] = sizing["stage2"][subsystem]
                except Exception as error:
                    print(f"\t\t!! {subsystem.capitalize()} sizing failed with: {error}")

        sized_dict: dict = {"stage1": {}, "stage2": {}}  # Dictionary with all sized classes
        if "engine" in self.selection:
            sizer("engine", run_engine_sizing, separate=True)

        if "recovery" in self.selection:
            sizer("recovery", run_recovery_sizing)

        if "structure" in self.selection:
            sizer("structure", run_structure_sizing)

        if "electronics" in self.selection:
            sizer("electronics", run_electronics_sizing)

        if not self.selection:
            if print_status:
                print("\t\tNo sizing options specified in the 'run_parameters.json'")

        for stage_name, stage_classes in sized_dict.items():
            for subsystem_name, subsystem_data in stage_classes.items():
                self.give_id(subsystem_data)
                self.new_rocket[stage_name][subsystem_name] = subsystem_data

        # Increase Rocket ID by 1
        serial_num = int(self.rocket.id)
        serial_num += 1
        self.new_rocket.id = serial_num

    def test_sizing(self):
        # run_electronics_sizing(copy.deepcopy(self.rocket))
        run_engine_sizing(copy.deepcopy(self.rocket), "stage1")
        # run_recovery_sizing(copy.deepcopy(self.rocket))
        # run_structure_sizing(copy.deepcopy(self.rocket))

    def show_plots(self, run_number: int):
        for variable in self.run_parameters["plot_selection"]:
            data = fm.load_variable(run_number, variable.split('.')[1:])
            print(variable, data)

    def check_rocket_class(self, new: bool = False):
        print("Checking Rocket Class")

        def check_level(obj):
            attributes = vars(obj)
            for attribute in attributes:
                if attribute != "simulator":
                    try:
                        attr_type = type(obj.__dict__[attribute])
                        if attr_type is float or attr_type is int or attr_type is str or attr_type is dict or\
                                attr_type is list or attr_type is np.array or attr_type is np.ndarray or attr_type is np.float64:
                            if obj.__dict__[attribute] is None:
                                print(f"\t\tAttribute '{attribute}' not defined! Please define an initial condition")
                                self.warnings += 1
                        else:
                            if obj.__dict__[attribute] is None:
                                print(f"\t\tAttribute '{attribute}' not defined! Please define an initial condition")
                                self.warnings += 1
                            else:
                                check_level(obj.__dict__[attribute])
                    except KeyError:
                        print(f"\t\tAttribute '{attribute}' not found in rocket class")

        if new:
            check_level(self.new_rocket)
        else:
            check_level(self.rocket)
        print(f"Rocket class checked; {self.warnings} warnings")

    def check_compliance(self, show_within_limit=False):
        print("Checking compliance with the requirements")

        def check_value(required_value, rocket_value, comparison_type, variable):
            def correct(difference, name):
                if show_within_limit:
                    print(f"\t{name} within limit; difference {difference}")

            def incorrect(difference, name):
                print(f"\t{name} out of limit! Difference {difference}")

            if str(comparison_type) == ">":
                if rocket_value > required_value:  # Correct
                    correct(rocket_value - required_value, variable)
                else:  # Incorrect
                    incorrect(rocket_value - required_value, variable)
            elif str(comparison_type) == "<":
                if rocket_value < required_value:  # Correct
                    correct(rocket_value - required_value, variable)
                else:  # Incorrect
                    incorrect(rocket_value - required_value, variable)
            elif str(comparison_type) == "=":
                if rocket_value == required_value:  # Correct
                    correct(rocket_value - required_value, variable)
                else:  # Incorrect
                    incorrect(rocket_value - required_value, variable)
            else:
                raise ValueError(f"Comparison type not well defined for variable {variable}")

        def add_line(system, line, rocket_sub):
            if len(system) > 1:
                rocket_sub = rocket_sub[system[0]]
                system.pop(0)
                add_line(system, line, rocket_sub)

            else:
                check_value(line["Value"], rocket_sub[line["Variable"]], line["Type"], line["Variable"])

        for index, row in self.requirements.iterrows():
            if int(row['Stage']) == 0:
                if row["Subsystem"] == "simulation":
                    check_value(row["Value"], self.rocket.simulator[row["Variable"]], row["Type"], row["Variable"])
                elif row["Subsystem"] == "rocket":
                    check_value(row["Value"], self.rocket[row["Variable"]], row["Type"], row["Variable"])
                else:
                    raise NameError(f"Subsystem '{row['Subsystem']}' is not recognised for compliance checking, use 'simulation' or 'rocket'")
            else:
                add_line(row["Subsystem"].split(", "), row, self.rocket[f"stage{int(row['Stage'])}"])

    def save_iteration(self):
        fm.export_rocket_iteration("rocket", self.new_rocket)

    def export_to_catia(self):
        fm.export_catia_parameters("catia", self.new_rocket, self.run_parameters["catia_variables"])

    def close(self):
        self.run_parameters_file.close()


if __name__ == "__main__":
    runner = Runner("initial_values")
    runner.run(5, testing=True)
    # runner.show_plots(1)
