import copy
import json
import os
import sys
import re

import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore
import time

import file_manager as fm
from simulators.advanced.aerodynamics import drag, isa
from simulators.advanced.dynamics import run as dynamics_run
from simulators.advanced.gravity import gravity
from simulators.simulator import Simulator

from sizing.engine import run as run_engine_sizing
from sizing.recovery import run as run_recovery_sizing
from sizing.electronics import run as run_electronics_sizing
from sizing.stability import run as run_stability_sizing
from sizing.engine import initialize as initialize_engines
from sizing.stability import initialize as initialize_stability
from sizing.rocket import Rocket


def extract_number(file):
    s = re.findall("\d+$",file)
    return int(s[0]) if s else 0, file


class Runner:
    def __init__(self, file_name: str):
        """
        :param file_name: Name of the rocket initialization file
        """
        print(sys.argv[0])
        self.current_file_path = os.path.split(sys.argv[0])[0]
        self.run_id: int = 0
        self.iteration_id: int = 0
        self.start_time: float = 0

        self.warnings: int = 0

        # Import the run parameters
        self.run_parameters_file = open(os.path.join(self.current_file_path, "files/run_parameters.json"))
        self.run_parameters: dict = json.load(self.run_parameters_file)
        self.selection: list[str] = self.run_parameters["sizing_selection"]

        simulator: Simulator = Simulator(self.run_parameters["mission_profile"], self.run_parameters["simulator_parameters"],
                                         dynamics_run, gravity, drag, isa)
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
        save_directory = os.path.join(self.current_file_path, f"files/archive")

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Make run_id based on last file created
        if os.listdir(save_directory) and not testing:
            self.run_id: int = int(max(os.listdir(f"{self.current_file_path}/files/archive"), key=extract_number).split("_")[1]) + 1
        else:
            self.run_id: int = 1

        # Check if file exists
        if not os.path.exists(f"{save_directory}/run_{self.run_id}"):
            os.makedirs(f"{save_directory}/run_{self.run_id}")

    def run(self, runs, save=True, print_iteration=True, print_sub=True, testing=False, export_catia=False, export_summary=False):
        print("Running Main Program")
        self.start_time = time.time()

        # Create an ID number to represent this run
        self.create_run_id(testing)

        # Save starting point
        if save:
            if print_sub:
                print("\tSaving Starting Point")
            if testing:
                fm.export_rocket_iteration(f"run_1/0000_rocket", self.new_rocket)
            else:
                fm.export_rocket_iteration(f"run_{self.run_id}/0000_rocket", self.new_rocket)

        # Run stability sizing before doing simulations
        initialize_stability(self.rocket)
        initialize_stability(self.new_rocket)

        # Check Rocket for missing parameters
        self.check_rocket_class()

        # Make sure all Subsystem parameters are summed into the Stages and main Rocket
        if print_sub:
            print("\tSumming Rocket Parameters")
        self.rocket.update(print_warnings=False)

        for i in range(runs):
            self.iteration_id = i + 1
            self.rocket.id = f"{self.run_id}.{self.iteration_id}"
            last_time = time.time()

            if print_iteration:
                print(f"Iteration {i + 1}/{runs}")

            # Simulation
            if print_sub:
                print("\tPopulating Simulation")
            self.populate_simulation()
            if print_sub:
                print("\tRunning Simulation")
            self.rocket.simulator.run()
            if self.iteration_id == 100:
                self.rocket.simulator.plot_trajectory()
            if print_sub:
                print(f"\t\tInitial apogee: {round(self.rocket.simulator.apogee, 3)} m")

            # Sizing
            self.run_sizing(print_sub)

            print(f"\tAltitude {self.rocket.simulator.apogee}")

            # Sum the Subsystems into the Stages and main Rocket
            if print_sub:
                print("\tSumming Rocket Parameters")
            self.new_rocket.update()

            # Save iteration
            if save:
                if print_sub:
                    print(Fore.RESET + "\tSaving Iteration")
                if testing:
                    fm.export_rocket_iteration(f"run_1/{str(self.iteration_id).zfill(4)}_rocket", self.new_rocket)
                else:
                    fm.export_rocket_iteration(f"run_{self.run_id}/{str(self.iteration_id).zfill(4)}_rocket", self.new_rocket)

            if export_catia:
                if print_sub:
                    print("\tExporting Catia File")
                self.export_to_catia()

            if export_summary:
                if print_sub:
                    print("\tExporting Summary")
                self.export_summary()

            # Overwrite old Rocket with New Rocket
            self.rocket = self.new_rocket

            if print_iteration:
                print(f"Finished iteration {i + 1}, after {round(time.time() - last_time, 2)} s")

        print(self.rocket.simulator.apogee_1)
        # Close
        print(f"Finished after {round(time.time() - self.start_time, 2)} s\n\tClosing program ...")
        self.close()

    def give_id(self, subsystem):
        serial_num = int(subsystem.id.split(".")[-1])
        serial_num += 1
        subsystem.id = f"{self.rocket.id}.{serial_num}"

    def populate_simulation(self):
        self.rocket.simulator.create_stages(self.rocket)

    def run_sizing(self, print_status=True):
        if print_status:
            print("\tRunning Sizing")

        flight_data = self.rocket.simulator.stages  # Flight data from the different stages
        self.rocket.simulator.delete_stages()

        changes: dict = {}

        def sizer(subsystem: str | list, function):
            if print_status:
                if type(subsystem) == list:
                    for system in subsystem:
                        print(f"\t\tSizing {system.capitalize()}")
                else:
                    print(f"\t\tSizing {subsystem.capitalize()}")

            rocket = copy.deepcopy(self.rocket)
            rocket.simulator.stages = flight_data

            # try:
            sizing = function(rocket)

            # Get all attributes from the Old and New version of the Rocket class
            old_rocket = self.rocket.export_all_values()
            new_rocket = sizing.export_all_values()

            for key, value in new_rocket.items():
                if not key == "simulator":
                    if type(value) == list or type(value) == np.array or type(value) == np.ndarray:
                        if not np.array_equal(new_rocket[key], old_rocket[key]):
                            if key not in changes:
                                changes[key] = value
                            else:
                                print(f"\t\t\tDuplicate in changes: '{key}'")
                    else:
                        if new_rocket[key] != old_rocket[key]:
                            if key not in changes:
                                changes[key] = value
                            else:
                                print(f"\t\t\tDuplicate in changes: '{key}'")
            # except Exception as error:
            #     print(f"\t\t!! {subsystem} sizing failed with: {error}")

        if "engine" in self.selection:
            sizer("engine", run_engine_sizing)

        if "recovery" in self.selection:
            sizer("recovery", run_recovery_sizing)

        if "electronics" in self.selection:
            sizer("electronics", run_electronics_sizing)

        if "stability" in self.selection:
            sizer("stability", run_stability_sizing)

        if not self.selection:
            if print_status:
                print("\t\tNo sizing options specified in the 'run_parameters.json'")

        def add_values(system, key, value):
            if "." in key:
                key_list = key.split(".")
                add_values(system[key_list[0]], '.'.join(key_list[1:]), value)
            else:
                system[key] = value

        for change_key, change_value in changes.items():
            add_values(self.new_rocket, change_key, change_value)

        # Increase Rocket ID by 1
        serial_num = int(self.rocket.id.split('.')[1])
        serial_num += 1
        self.new_rocket.id = f"{self.run_id}.{serial_num}"

    def test_sizing(self):
        # run_electronics_sizing(copy.deepcopy(self.rocket))
        # run_engine_sizing(copy.deepcopy(self.rocket), "stage1")
        # run_recovery_sizing(copy.deepcopy(self.rocket))
        # run_structure_sizing(copy.deepcopy(self.rocket))
        run_stability_sizing(copy.deepcopy(self.rocket))

    def show_plots(self, run_number: int):
        for variable in self.run_parameters["plot_selection"]:
            data = fm.load_variable(run_number, variable.split('.')[1:])
            plt.plot(np.arange(0, len(data)), data)
            plt.title(str(variable))
            plt.show()

    def check_rocket_class(self, new: bool = False, general_print: bool = False):
        print("Checking Rocket Class")

        def check_level(obj, name):
            attributes = vars(obj)
            for key, attribute in attributes.items():
                if key != "simulator":
                    if key in self.rocket.compare_list or key in self.rocket.excluded_variables:
                        if attribute is None:
                            if general_print:
                                print(Fore.YELLOW + f"\t\tAttribute '{name}.{key}' not defined!")

                    else:
                        try:
                            attr_type = type(attribute)
                            if attr_type is float or attr_type is int or attr_type is str or attr_type is dict or\
                                    attr_type is list or attr_type is np.array or attr_type is np.ndarray or attr_type is np.float64:
                                if attribute is None:
                                    print(Fore.YELLOW + f"\t\tAttribute '{name}.{key}' not defined! Please define an initial condition")
                                    self.warnings += 1
                            else:
                                if attribute is None:
                                    print(Fore.YELLOW + f"\t\tAttribute '{name}.{key}' not defined! Please define an initial condition")
                                    self.warnings += 1
                                else:
                                    check_level(attribute, f"{name}.{key}")
                        except KeyError:
                            print(Fore.YELLOW + f"\t\tAttribute '{name}.{key}' not found in rocket class")

        if new:
            check_level(self.new_rocket, "NewRocket")
        else:
            check_level(self.rocket, "OldRocket")
        print(Fore.RESET + f"Rocket class checked; {self.warnings} warnings")

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
        fm.export_to_csv("catia", f"catia_{self.run_id}", self.new_rocket, self.run_parameters["catia_variables"])

    def export_summary(self):
        fm.export_to_csv("summaries", f"summary_{self.run_id}", self.new_rocket, {})

    def close(self):
        self.run_parameters_file.close()


if __name__ == "__main__":
    runner = Runner("initial_values_2")
    # runner.test_sizing()
    runner.run(100, export_summary=True)
    # runner.show_plots(7)
