import matplotlib.pyplot as plt
import numpy as np

colours = ["#00A6D6", "#EC6842", "#A50034", "#009B77"]
line_types = ["-", "--", "-.", ":"]


def plot_2d(data_set: list[dict] | dict, x_lim: tuple = (0, None), y_lim: tuple = (0, None), show_change: bool = False):
    labels: dict = {"x_label": None, "y_label": None}
    legend_available: bool = False

    # Fix Limits
    if not x_lim:
        x_lim = (0, None)
    if not y_lim:
        y_lim = (0, None)
    if x_lim[0] == "None":
        x_lim = (None, x_lim[1])
    if x_lim[1] == "None":
        x_lim = (x_lim[0], None)
    if y_lim[0] == "None":
        y_lim = (None, y_lim[1])
    if y_lim[1] == "None":
        y_lim = (y_lim[0], None)

    x_loc = x_lim
    y_loc = y_lim
    for coordinates in data_set:
        if show_change:
            if coordinates["x_data"] is None:
                coordinates["x_data"] = np.arange(0, len(coordinates["y_data"]))
            if coordinates["y_data"] is None:
                coordinates["y_data"] = np.arange(0, len(coordinates["x_data"]))

            if x_loc[0] is None:
                x_loc = (coordinates["x_data"][0], x_loc[1])
            elif coordinates["x_data"][0] < x_loc[0]:
                x_loc = (coordinates["x_data"][0], x_loc[1])

            if x_loc[1] is None:
                x_loc = (x_loc[0], coordinates["x_data"][1])
            elif coordinates["x_data"][-1] > x_loc[1]:
                x_loc = (coordinates["x_data"][0], x_loc[1])

            if y_loc[0] is None:
                y_loc = (coordinates["y_data"][0], y_loc[1])
            elif coordinates["y_data"][0] < y_loc[0]:
                y_loc = (coordinates["x_data"][0], y_loc[1])

            if y_loc[1] is None:
                y_loc = (y_loc[0], coordinates["y_data"][1])
            elif coordinates["y_data"][-1] > y_loc[1]:
                y_loc = (coordinates["y_data"][0], y_loc[1])

    for i, data in enumerate(data_set):
        if i == 0:
            labels["x_label"] = data["x_description"]
            labels["y_label"] = data["y_description"]
        if data["x_data"] is None:
            data["x_data"] = np.arange(0, len(data["y_data"]))
        if data["y_data"] is None:
            data["y_data"] = np.arange(0, len(data["x_data"]))

        if show_change:
            percentual_change = round(abs(data["y_data"][x_loc[1]] - data["y_data"][x_loc[1] - 1]) / data["y_data"][x_loc[1] - 1] * 100, 3)
            x_location = x_loc[1] - 0.12 * (x_loc[1] - x_loc[0])
            y_location = data["y_data"][-1] - 0.04 * (y_loc[1] - y_loc[0])
            plt.text(x_location, y_location, f"{percentual_change}%")

        plt.plot(data["x_data"], data["y_data"], label=data["name"], color=colours[i], linestyle=line_types[i])

        if data["name"]:
            legend_available = True

    plt.xlabel(labels["x_label"])
    plt.ylabel(labels["y_label"])

    plt.xlim(x_lim)
    plt.ylim(y_lim)

    plt.minorticks_on()
    plt.grid()
    if legend_available:
        plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    set1 = {"x_description": "Iteration [-]", "x_data": [0, 1, 2, 3, 5, 7],
            "y_description": "Mass [kg]", "y_data": [2, 1, 5, 3, 6, 8], "name": "test1"}

    set2 = {"x_description": "Iteration [-]", "x_data": [0, 1, 2, 3, 5, 7],
            "y_description": "Mass [kg]", "y_data": [0, 1, 7, 2, 4, 5], "name": "test1"}

    plot_2d([set1, set2, set2, set1])
