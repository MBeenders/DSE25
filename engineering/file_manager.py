from sizing.rocket import Rocket
from simulators.simulator import Simulator
import pandas as pd
import pickle
import json
import os
import sys


current_file_path = os.path.split(sys.argv[0])[0]


def import_chemical(chemical_name: str) -> dict:
    """
    :param chemical_name: Name of the chemical
    :return: Dictionary with information about the chemical
    """
    chemical_file = open(os.path.join(current_file_path, f"files/chemicals/{chemical_name}.json"))
    return json.load(chemical_file)


def import_engine_chemicals(engine_stages: dict, rocket: Rocket):
    """
    :param engine_stages: Dictionary with the different engine stages and their respective oxidizer and fuel names
    :param rocket: The Rocket class
    """
    for stage_name, engine_chemicals in engine_stages.items():
        for chemical_type, chemical in engine_chemicals.items():
            rocket[stage_name]["engine"][chemical_type] = import_chemical(chemical)


def import_csv(file_name: str) -> pd.DataFrame:
    """
    :param file_name: Name of csv file, must be in "files" folder
    :return: Pandas dataframe of the file
    """
    return pd.read_csv(os.path.join(current_file_path, f"files/{file_name}.csv"))


def insert_values(data: pd.DataFrame, rocket: Rocket):
    """
    :param data: Pandas Dataframe file with initialization values
    :param rocket: Rocket class
    """

    def add_value(current_value, variable, rocket_sub):
        try:  # Check if variable exists
            try:  # Try to convert it to a float, otherwise leave it as a string
                value = float(current_value)
            except ValueError:
                value = current_value

            rocket_sub[variable] = value
        except KeyError as error:
            raise Exception(f"'{current_value}' not found in csv, error: {error}")

    def add_line(subsystem, line, rocket_sub):
        if len(subsystem) > 1:  # Dig deeper into the class system to get to the subclass
            try:
                rocket_sub = rocket_sub[subsystem[0]]
            except KeyError as error:
                raise Exception(f"Subsystem '{subsystem[0]}' not found in Rocket class, error: {error}")

            subsystem.pop(0)
            add_line(subsystem, line, rocket_sub)

        else:  # Insert the value under the right variable
            add_value(line["Value"], line["Variable"], rocket_sub[subsystem[0]])

    for index, row in data.iterrows():
        if row["Subsystem"] == "rocket":  # If it is a global rocket value
            add_value(row["Value"], row["Variable"], rocket)
        elif row["Subsystem"] == "stage":  # If it is a stage value
            add_value(row["Value"], row["Variable"], rocket[f"stage{int(row['Stage'])}"])
        else:  # If it is a subsystem value
            add_line(row["Subsystem"].split(","), row, rocket[f"stage{int(row['Stage'])}"])


def initialize_rocket(file_name: str, simulator: Simulator, run_parameters: dict) -> Rocket:
    """
    :param file_name: Name of csv file, must be in "files" folder
    :param simulator: The trajectory simulator
    :param run_parameters: The parameters that decide what the program will run
    :return: A filled Rocket class
    """
    data = import_csv(file_name)  # Import initialization data
    rocket = Rocket(simulator)  # Initialize rocket

    insert_values(data, rocket)  # Insert csv values into Rocket class

    import_engine_chemicals(run_parameters["engine_chemicals"], rocket)

    return rocket


def import_rocket_iteration(file_name: str) -> Rocket:
    """
    :param file_name: Name of the file that needs to be imported
    :return Rocket class
    Imports a Rocket class from a previous iteration
    """
    with open(os.path.join(current_file_path, f"files/{file_name}.pickle"), 'rb') as file:
        return pickle.load(file)


def export_rocket_iteration(file_name: str, rocket: Rocket):
    """
    :param file_name: Name under which the file will be exported
    :param rocket: The filled Rocket class
    Saves the entire class in the archive as a pickle file.
    """

    rocket.simulator.delete_stages()
    with open(os.path.join(current_file_path, f"files/archive/{file_name}.pickle"), 'wb') as file:
        pickle.dump(rocket, file)


def export_to_csv(folder_name: str, file_name: str, rocket: Rocket, variables: dict):
    """
    :param folder_name: Directory name of the file the csv will be saved in
    :param file_name: Name under which the file will be exported
    :param rocket: The filled Rocket class
    :param variables: A list of strings linked to the variables that will be exported to catia
    """

    parameters: dict = {"iteration": str(rocket.id)}

    def get_info(total_name, item, subsystem: Rocket):
        if type(item) == dict:
            for key2, item2 in item.items():
                get_info(f"{total_name}_{key2}", item2, subsystem[key2])

        else:
            parameters[f"{total_name} {item}"] = subsystem

    if variables:
        for name, value in variables.items():
            get_info(name, value, rocket[name])
    else:
        parameters = rocket.export_all_values()

    data = pd.DataFrame.from_dict(parameters, orient="index").transpose()
    output_dir = os.path.join(current_file_path, f"files/{folder_name}")
    output_path = os.path.join(current_file_path, f"files/{folder_name}/{file_name}.csv")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    data.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


def load_variable(run_number: int, variable: list):
    data: list = []

    def get_variable(rocket, i):
        i += 1
        if len(variable) == i + 1:
            data.append(rocket[variable[i]])
        else:
            get_variable(rocket[variable[i]], i)

    files = os.listdir(os.path.join(current_file_path, f"files/archive/run_{run_number}"))
    for file in files:
        iteration = import_rocket_iteration(f"archive/run_{run_number}/{file.split('.')[0]}")
        get_variable(iteration, -1)

    return data


if __name__ == "__main__":
    pass
