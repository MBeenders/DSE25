import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json


class GanttChartGenerator:
    def __init__(self, file_name: str, style: str, figure_size=(11.7, 16.5), start_count: int = 0):
        self.figure, self.ax = plt.subplots(1, figsize=figure_size)
        self.ax_top = self.ax.twiny()

        self.start_count = start_count

        with open(f"styles/{style}.json") as style_file:
            self.style: dict = json.load(style_file)

        self.data = pd.read_csv(f"management/gantt_chart/files/{file_name}.csv",
                                parse_dates=['Started', 'Due'], dayfirst=True)

        self.amount_of_tasks = len(self.data["Task"].tolist())

    @staticmethod
    def __add_spaces(frame):
        longest_string = frame.Code.str.len().max()
        codes = []
        for index, row in frame.iterrows():
            codes.append(row.Code.rjust(longest_string))

        return codes

    def __change_to_initials(self):
        initials_register = {"Charlie Kendall": "CK",
                             "Daniël Norbart": "DN",
                             "Elvin Chen": "EC",
                             "Laura Tabaksblat": "LT",
                             "Luca Alonso": "LA",
                             "Martijn Rusch": "MR",
                             "Mauro Beenders": "MB",
                             "Sarissa Aurori": "SA",
                             "Stef": "SY",
                             "Thijmen Odijk": "TO"}

        initials = []
        for index, row in self.data.iterrows():
            assignees = []
            if isinstance(row["Responsible"], str):
                for person in row["Responsible"].split(", "):
                    assignees.append(initials_register[person])
            else:
                assignees.append(" ")
            initials.append(', '.join(assignees))

        self.data["Initials"] = initials

    def __add_colour(self):
        colour_row = []
        for index, row in self.data.iterrows():
            task_type = row["Code"].count(".")
            if task_type == 0:
                colour_row.append(self.style["colors"]["HEX"]["Primary"])
            elif task_type == 1:
                colour_row.append(self.style["colors"]["HEX"]["Secondary_01"])
            elif task_type == 2:
                colour_row.append(self.style["colors"]["HEX"]["Secondary_02"])
            elif task_type == 3:
                if "Document" in row["Task"]:
                    colour_row.append(self.style["colors"]["HEX"]["Secondary_03"])
                else:
                    colour_row.append(self.style["colors"]["HEX"]["Secondary_04"])
            else:
                print(row)
                raise

        self.data['colour'] = colour_row

    def __calculate_dates(self):
        # project start date
        self.project_start = self.data.Started.min()
        # number of days from project start to task start
        self.data['start_num'] = (self.data.Started - self.project_start).dt.days
        # number of days from project start to end of tasks
        self.data['end_num'] = (self.data.Due - self.project_start).dt.days + 1
        # days between start and end of each task
        self.data['days_start_to_end'] = self.data.end_num - self.data.start_num

    def __add_description(self):
        code_list = self.__add_spaces(self.data)
        description_data = np.array([self.data.Task.tolist(), code_list,
                                     self.data.Initials.tolist(), self.data["Hours"].tolist()]).T
        descriptions = []
        max_indent = 4
        for row in description_data:
            indent = row[1].count('.')
            task = f'{row[1].strip()}. {row[0]}'
            changed = f'{" " * indent}{task:<57}{" " * (max_indent - indent)}{row[2]:>10}{row[3]:>10}'
            descriptions.append(changed)

        self.data["Description"] = descriptions

    def __sort_data(self):
        weights = [100 ** 4, 100 ** 3, 100 ** 2, 100, 1]
        self.data = self.data.sort_values("Code", key=lambda ser: ser.apply(lambda x: -sum([weights[idx] * int(val) for idx, val in enumerate(x.split("."))])), ignore_index=True)

    def __add_row_number(self):
        max_index = len(self.data.index) + self.start_count
        descriptions = []
        for index, row in self.data.iterrows():
            descriptions.append(f'{max_index - index:<4} {row["Description"]}')
        self.data['Description'] = descriptions

    def __add_weekends(self):
        for weekend in range(9):
            self.ax.barh(np.arange(self.amount_of_tasks), 2, height=1, left=(5 + 7 * weekend), color="#e6e6e6")

    def __add_tasks(self):
        self.ax.barh(self.data.Description, self.data.days_start_to_end, left=self.data.start_num, color=self.data.colour)

    def __add_ticks(self):
        self.ax.get_xaxis().set_visible(False)
        for tick in self.ax.get_xticklabels():
            tick.set_fontname(self.style["fonts"]["gantt_chart"]["family"])
        for tick in self.ax.get_yticklabels():
            tick.set_fontname(self.style["fonts"]["gantt_chart"]["family"])

    def __top_axis(self):
        # Align x axis
        self.ax.set_xlim(0, self.data.end_num.max())
        self.ax_top.set_xlim(0, self.data.end_num.max())

        # Top ticks (markings)
        x_ticks_top_minor = np.arange(0, self.data.end_num.max() + 1, 7)
        self.ax_top.set_xticks(x_ticks_top_minor, minor=True)
        # Top ticks (label)
        self.ax_top.set_xticks([])
        # Week labels
        x_ticks_top_labels = []
        for week in range(1, len(x_ticks_top_minor) + 1):
            x_ticks_top_labels.append(f"Week {week}\n"
                                      f"{(self.project_start + (week - 1) * pd.Timedelta(days=7)).strftime('%d/%m/%y')}")
        # x_ticks_top_labels.append([f"Week {i}"for i in np.arange(1, len(xticks_top_major)+1, 1)])
        self.ax_top.set_xticklabels(x_ticks_top_labels, rotation=0, ha='left', minor=True)

        # Grid lines
        self.ax_top.set_axisbelow(True)
        self.ax_top.xaxis.grid(color='gray', linestyle='dashed', alpha=0.3, which='minor')
        self.ax_top.xaxis.grid(which='major', color='k', linestyle='dashed', alpha=0.3)

        # Set tick lengths and color equal for major and minor ticks
        self.ax_top.tick_params(which='major', color='k', length=2)
        self.ax_top.tick_params(which='minor', length=2, color='k')

        # Minor ticks each day, major ticks each week
        minor_ticks = [x for x in range(0, 9 * 7 + 6) if x % 7 != 0]
        minor_labels = ['T', 'W', 'T', 'F', 'S', 'S'] * 9 + ['T', 'W', 'T', 'F', '']
        major_ticks = list(range(0, 9 * 7 + 5, 7))
        major_labels = ['M'] * 10
        self.ax_top.set_xticks(minor_ticks, minor=True, labels=minor_labels, fontsize=6, ha='left')
        self.ax_top.set_xticks(major_ticks, labels=major_labels, fontsize=6, ha='left')
        self.ax_top.tick_params(axis='x', which='major', pad=0)
        self.ax_top.tick_params(axis='x', which='minor', pad=0)

        # Add "Week i" labels
        n = 7 * 9 + 5
        for i in range(9):
            x = 1 / n * (7 * i + 3.5)
            self.ax_top.text(x, 1.008, f'Week {i + 1}', transform=self.ax_top.transAxes, fontsize=9, ha='center')
        self.ax_top.text(1 / n * (7 * 9 + 2.5), 1.008, 'Week 10', transform=self.ax_top.transAxes, ha='center', fontsize=9)

    def __add_column_names(self):
        self.ax_top.text(-0.255, 1.002, 'Task', transform=self.ax_top.transAxes, fontsize=8)
        self.ax_top.text(-0.12, 1.002, 'Person', transform=self.ax_top.transAxes, fontsize=8)
        self.ax_top.text(-0.05, 1.002, 'Time', transform=self.ax_top.transAxes, fontsize=8)

    def __color_descriptions(self):
        for tl in self.ax.get_yticklabels():
            tl.set(fontsize=6)
            tl.set_linespacing(1.0)
            txt = tl.get_text()
            if txt[6:8] == '. ':
                txt += ' (!)'
                tl.set_bbox(dict(facecolor=self.style["colors"]["HEX"]["Primary"], edgecolor='none', pad=2))
                tl.set(color=self.style["colors"]["HEX"]["Text_Light"])
            elif txt[9:11] == '. ':
                txt += ' (!)'
                tl.set_bbox(dict(facecolor=self.style["colors"]["HEX"]["Secondary_01"], edgecolor='none', pad=2))
                tl.set(color=self.style["colors"]["HEX"]["Text_Light"])
            tl.set_text(txt)

    def __refresh_limits(self):
        n = len(self.data.index)
        self.ax.set_ylim(-0.5, n - 0.5)

        self.ax.set_xlim(0, self.data.end_num.max())
        self.ax_top.set_xlim(0, self.data.end_num.max())

    def run(self):
        self.__calculate_dates()
        self.__change_to_initials()
        self.__add_description()
        self.__add_colour()
        self.__sort_data()
        self.__add_row_number()
        self.__add_weekends()
        self.__add_tasks()
        self.__add_ticks()
        self.__top_axis()
        self.__add_column_names()
        self.__color_descriptions()
        self.__refresh_limits()

        self.figure.tight_layout()
        plt.savefig('management/gantt_chart/output/test.pdf')


generator = GanttChartGenerator("file_09_b", "tudelft_house_style")
generator.run()
