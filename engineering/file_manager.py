from sizing.rocket import Rocket
import pandas as pd
import os


def import_csv(file_name: str) -> pd.DataFrame:
    """
    :param file_name: Name of csv file, must be in "files" folder
    :return: Pandas dataframe of the file
    """
    return pd.read_csv(os.path.join("files", f'{file_name}.csv'))


def insert_values(data: pd.DataFrame, rocket: Rocket):
    """
    :param data: Pandas Dataframe file with initialization values
    :param rocket: Rocket class
    """
    rocket_subsystem = rocket

    def add_line(subsystem, line, rocket_sub):
        if len(subsystem) > 1:
            rocket_sub = rocket_sub[subsystem[0]]
            subsystem.pop(0)
            add_line(subsystem, line, rocket_sub)

        else:
            rocket_sub[subsystem[0]][line["Variable"]] = line["Value"]

    for index, row in data.iterrows():
        add_line(row["Subsystem"].split(", "), row, rocket_subsystem)


def initialize_rocket(file_name: str):
    """
    :param file_name: Name of csv file, must be in "files" folder
    :return: A filled Rocket class
    """
    data = import_csv(file_name)  # Import initialization data
    rocket = Rocket()  # Initialize rocket

    insert_values(data, rocket)  # Insert csv values into Rocket class

    return rocket


def export_catia_parameters(file_name: str, rocket: Rocket):
    """
    :param file_name: Name under which the file will be exported
    :param rocket: The filled Rocket class
    """
    pass


if __name__ == "__main__":
    initialize_rocket("initial_values")
