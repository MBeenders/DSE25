import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np


class Square:
    def __init__(self, severity: int, probability: int):
        self.severity = severity
        self.probability = probability

        self.risks: list = []


def convert_csv(name: str):
    data = pd.read_csv(f"management/risk_map/files/{name}.csv")

    converted_data: dict = {}
    for index, row in data.iterrows():
        if row["Risk ID"] != "":
            converted_data[row["Risk ID"]] = {"Probability": int(row["Probability"]), "Severity": int(row["Severity"])}

    return converted_data


def convert_to_list(data: dict):
    converted_index: list = []
    converted_row: list = []
    for index, row in data.items():
        converted_index.append(index)
        converted_row.append(row)

    return converted_index, converted_row


class RiskMapGenerator:
    def __init__(self, file_start: str, style: str, csv: bool = False):
        self.directory_start = file_start
        self.figure, self.ax = plt.subplots(figsize=(10, 5))

        with open(f"styles/{style}.json") as style_file:
            self.style: dict = json.load(style_file)

        if csv:
            self.risks = convert_csv(file_start)

        else:
            with open(f"management/risk_map/files/{file_start}.json") as risk_file:
                self.risks: dict = json.load(risk_file)

        self.squares: list = []

    def __create_plot(self):
        for severity in range(1, 6):
            for probability in range(1, 4):
                self.squares.append(Square(severity, probability))

        for index, item in self.risks.items():
            for square in self.squares:
                if square.probability == item["Probability"] and square.severity == item["Severity"]:
                    square.risks.append(index)

    def __add_labels(self):
        wrap_at = 5
        for severity in range(1, 6):
            for probability in range(1, 4):
                for square in self.squares:
                    if square.probability == probability and square.severity == severity:
                        sorted_risks = sorted(square.risks)
                        for k, risk in enumerate(sorted_risks):
                            self.ax.text((probability - 0.48 + 0.2 * (k % wrap_at)), (severity + 0.3 - 0.025 * k + 0.025 * (k % wrap_at)), risk[8:], fontsize=8)

    def __add_background(self):
        # High Column
        self.ax.fill([2.5, 2.5, 3.5, 3.5],
                     [4.5, 5.5, 5.5, 4.5], color=self.style["colors"]["HEX"]["Secondary_02"], alpha=0.2)
        self.ax.fill([2.5, 2.5, 3.5, 3.5],
                     [3.5, 4.5, 4.5, 3.5], color=self.style["colors"]["HEX"]["Secondary_06"], alpha=0.2)
        self.ax.fill([2.5, 2.5, 3.5, 3.5],
                     [2.5, 3.5, 3.5, 2.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([2.5, 2.5, 3.5, 3.5],
                     [1.5, 2.5, 2.5, 1.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([2.5, 2.5, 3.5, 3.5],
                     [0, 1.5, 1.5, 0], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)

        # Medium Column
        self.ax.fill([1.5, 1.5, 2.5, 2.5],
                     [4.5, 5.5, 5.5, 4.5], color=self.style["colors"]["HEX"]["Secondary_06"], alpha=0.2)
        self.ax.fill([1.5, 1.5, 2.5, 2.5],
                     [3.5, 4.5, 4.5, 3.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([1.5, 1.5, 2.5, 2.5],
                     [2.5, 3.5, 3.5, 2.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([1.5, 1.5, 2.5, 2.5],
                     [1.5, 2.5, 2.5, 1.5], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)
        self.ax.fill([1.5, 1.5, 2.5, 2.5],
                     [0, 1.5, 1.5, 0], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)

        # Low Column
        self.ax.fill([0, 0, 1.5, 1.5],
                     [4.5, 5.5, 5.5, 4.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([0, 0, 1.5, 1.5],
                     [3.5, 4.5, 4.5, 3.5], color=self.style["colors"]["HEX"]["Secondary_03"], alpha=0.2)
        self.ax.fill([0, 0, 1.5, 1.5],
                     [2.5, 3.5, 3.5, 2.5], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)
        self.ax.fill([0, 0, 1.5, 1.5],
                     [1.5, 2.5, 2.5, 1.5], color=self.style["colors"]["HEX"]["Secondary_10"], alpha=0.2)
        self.ax.fill([0, 0, 1.5, 1.5],
                     [0, 1.5, 1.5, 0], color=self.style["colors"]["HEX"]["Secondary_11"], alpha=0.2)

    def run(self):
        # self.__create_plot(self.risks_after, after=True)
        # self.__add_labels(self.risks_after, self.after_labels)
        self.__create_plot()
        self.__add_labels()
        self.__add_background()

        self.ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.set_xlim(0.5, 3.5)
        self.ax.set_ylim(0.5, 5.5)

        plt.xlabel("Probability", weight='bold')
        plt.ylabel("Severity", weight='bold')
        plt.xticks([1, 2, 3], ['Low', 'Medium', 'High'])
        plt.yticks([1, 2, 3, 4, 5], ['Very low', 'Low', 'Medium', 'High', 'Severe'])
        plt.tight_layout()
        plt.savefig(f'management/risk_map/output/{self.directory_start}.pdf')
        # plt.show()


generator = RiskMapGenerator("technical_risks_before_3", "tudelft_house_style", csv=True)
generator.run()
