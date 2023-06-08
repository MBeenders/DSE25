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
    chemical_file = open(f"{current_file_path}/files/chemicals/{chemical_name}.json")
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
    return pd.read_csv(f"{current_file_path}/files/{file_name}.csv")


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
    with open(f"{current_file_path}/files/{file_name}.pickle", 'rb') as file:
        return pickle.load(file)


def export_rocket_iteration(file_name: str, rocket: Rocket, run_id: int):
    """
    :param file_name: Name under which the file will be exported
    :param rocket: The filled Rocket class
    :param run_id: ID of the current run
    Saves the entire class in the archive as a pickle file.
    """
    with open(f"{current_file_path}/files/archive/{file_name}_{run_id}.{rocket.id}.pickle", 'wb') as file:
        pickle.dump(rocket, file)


def export_catia_parameters(file_name: str, rocket: Rocket, variables: dict):
    """
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

    for name, value in variables.items():
        get_info(name, value, rocket[name])

    data = pd.DataFrame.from_dict(parameters, orient="index").transpose()
    output_path = f"{current_file_path}/files/catia/{file_name}.csv"
    data.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


if __name__ == "__main__":
    pass
