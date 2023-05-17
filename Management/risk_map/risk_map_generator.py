import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np


def convert_csv(name: str):
    data = pd.read_csv(f"management/risk_map/files/{name}.csv")

    converted_data: dict = {}
    for index, row in data.iterrows():
        if row["Risk ID"] != "":
            converted_data[row["Risk ID"]] = {"Probability": row["Probability"], "Severity": row["Severity"]}

    return converted_data


def convert_to_list(data: dict):
    converted_index: list = []
    converted_row: list = []
    for index, row in data.items():
        converted_index.append(index)
        converted_row.append(row)

    return converted_index, converted_row


class RiskMapGenerator:
    def __init__(self, file_start: str, style: str, file_after: str = None, csv: bool = False):
        self.figure, self.ax = plt.subplots()

        with open(f"styles/{style}.json") as style_file:
            self.style: dict = json.load(style_file)

        if csv:
            self.risks_start = convert_csv(file_start)

            if file_after:
                self.risks_after = convert_csv(file_after)
        else:
            with open(f"management/risk_map/files/{file_start}.json") as risk_file:
                self.risks_start: dict = json.load(risk_file)

            if file_after:
                with open(f"management/risk_map/files/{file_after}.json") as risk_file:
                    self.risks_after: dict = json.load(risk_file)

        self.indexes, self.rows = convert_to_list(self.risks_start)

        self.start_labels = np.zeros((5, 5, len(self.risks_start)), dtype=int)
        if file_after:
            self.after_labels = np.zeros((5, 5, len(self.risks_after)), dtype=int)

    def __create_plot(self, risks, after: bool = False):
        i = 0
        for name, risk in risks.items():
            i += 1
            if int(risk["Probability"]) * int(risk["Severity"]) > 16:
                colour = self.style["colors"]["HEX"]["Secondary_02"]
            elif int(risk["Probability"]) * int(risk["Severity"]) > 11:
                colour = self.style["colors"]["HEX"]["Secondary_06"]
            elif int(risk["Probability"]) * int(risk["Severity"]) > 4:
                colour = self.style["colors"]["HEX"]["Secondary_03"]
            elif int(risk["Probability"]) * int(risk["Severity"]) > 2:
                colour = self.style["colors"]["HEX"]["Secondary_10"]
            else:
                colour = self.style["colors"]["HEX"]["Secondary_11"]
            self.ax.scatter(int(risk["Probability"]), int(risk["Severity"]), c=colour)

            if after:
                self.after_labels[risk["Severity"] - 1][risk["Probability"] - 1][int(name.split("-")[-1]) - 1] = i
            else:
                self.start_labels[risk["Severity"] - 1][risk["Probability"] - 1][int(name.split("-")[-1]) - 1] = i

    def __add_labels(self, risks, labels):
        wrap_at = 4
        for i in range(len(labels)):
            for j in range(len(labels[i])):
                non_zeros = labels[i][j][labels[i][j] != 0]
                row_offset = (len(non_zeros) - 1) * (0.09 / (len(non_zeros % wrap_at) + 1))
                for k, value in enumerate(non_zeros):
                    if k <= wrap_at - 1:
                        self.ax.text((j + 1.1), (i + 1 + row_offset - k * 0.18 - 0.05), self.indexes[value - 1][8:], fontsize=9)
                    else:
                        self.ax.text((j + 1.45), (i + 1 + row_offset - (k-wrap_at) * 0.18 - 0.05), self.indexes[value - 1][8:], fontsize=9)

    def __add_background(self):
        self.ax.fill([0, 0, 12, 9.02],
                     [9.02, 12, 0, 0], color=self.style["colors"]["HEX"]["Secondary_02"], alpha=0.2)
        self.ax.fill([0, 0, 9, 7.02],
                     [7.02, 9, 0, 0], color=self.style["colors"]["HEX"]["Secondary_06"], alpha=0.2)
        self.ax.fill([0, 0, 7, 5.02],
                     [5.02, 7, 0, 0], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([0, 0, 5, 3.02],
                     [3.02, 5, 0, 0], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)
        self.ax.fill([0, 0, 3],
                     [0, 3, 0], color=self.style["colors"]["HEX"]["Secondary_11"], alpha=0.2)

    def run(self):
        # self.__create_plot(self.risks_after, after=True)
        # self.__add_labels(self.risks_after, self.after_labels)
        self.__create_plot(self.risks_start, after=False)
        self.__add_labels(self.risks_start, self.start_labels)
        self.__add_background()

        self.ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.set_xlim(0.5, 3.5)
        self.ax.set_ylim(0.5, 5.5)

        plt.xlabel("Probability")
        plt.ylabel("Severity")
        plt.tight_layout()
        plt.savefig('management/risk_map/output/technical_risks_after.pdf')
        # plt.show()


generator = RiskMapGenerator("technical_risks_after", "tudelft_house_style", csv=True)
generator.run()
