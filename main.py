import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

data = pd.read_csv("files/file_04.csv", parse_dates=['Started', 'Due'], dayfirst=True)
print(data.columns)

font = {'family': 'Arial',
        'color': 'black',
        'weight': 'normal',
        'size': 11}


def change_to_initials(frame):
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
    for index, row in frame.iterrows():
        assignees = []
        if isinstance(row["Responsible"], str):
            for person in row["Responsible"].split(", "):
                assignees.append(initials_register[person])
        else:
            assignees.append(" ")
        initials.append(', '.join(assignees))

    frame["Initials"] = initials


def add_colour(frame):
    colour_row = []
    for index, row in frame.iterrows():
        task_type = row["Code"].count(".")
        if task_type == 0:
            colour_row.append("#DAE8FC")
        elif task_type == 1:
            colour_row.append("#E1D5E7")
        elif task_type == 2:
            colour_row.append("#F8CECC")
        elif task_type == 3:
            colour_row.append("#FFF2CC")
        else:
            raise False

    frame['colour'] = colour_row


def add_spaces(frame):
    longest_string = frame.Code.str.len().max()
    codes = []
    for index, row in frame.iterrows():
        codes.append(row.Code.rjust(longest_string))

    return codes


# project start date
project_start = data.Started.min()
# number of days from project start to task start
data['start_num'] = (data.Started - project_start).dt.days
# number of days from project start to end of tasks
data['end_num'] = (data.Due - project_start).dt.days + 1
# days between start and end of each task
data['days_start_to_end'] = data.end_num - data.start_num

# Change to initials
change_to_initials(data)

# Description
code_list = add_spaces(data)
description_data = np.array([data.Task.tolist(), code_list, data.Initials.tolist(), data["Hours"].tolist()]).T
descriptions = []
for row in description_data:
    changed = "{: >35} {: >10} {: >5} {: >5}".format(*row)
    descriptions.append(changed)

data["Description"] = descriptions
amount_of_tasks = len(data["Task"].tolist())

add_colour(data)

weights = [100**4, 100**3, 100**2, 100, 1]
data = data.sort_values("Code", key=lambda ser: ser.apply(lambda x: -sum([weights[idx] * int(val) for idx, val in enumerate(x.split("."))])))
# data = data.sort_values(["Code"], ascending=[False])

fig, ax1 = plt.subplots(1, figsize=(16, 6))

# Add weekends
for weekend in range(9):
    ax1.barh(np.arange(amount_of_tasks), 2, height=1, left=(5 + 7*weekend), color="#e6e6e6")
ax1.barh(data.Description, data.days_start_to_end, left=data.start_num, color=data.colour)

# Ticks
ax1.get_xaxis().set_visible(False)
# xticks = np.arange(0, data.end_num.max()+1, 3)
# xticks_labels = pd.date_range(project_start, end=data.Due.max()).strftime("%d/%m")
# xticks_minor = np.arange(0, data.end_num.max()+1, 1)
# ax1.set_xticks(xticks)
# ax1.set_xticks(xticks_minor, minor=True)
# ax1.set_xticklabels(xticks_labels[::3])

# for label in ax1.get_xticklabels():
#     label.set_horizontalalignment('left')
#     label.set_rotation(-40)

# Set the font name for axis tick labels to be Comic Sans
for tick in ax1.get_xticklabels():
    tick.set_fontname("Arial")
for tick in ax1.get_yticklabels():
    tick.set_fontname("Arial")

# Top axis
ax_top = ax1.twiny()

# Align x axis
ax1.set_xlim(0, data.end_num.max())
ax_top.set_xlim(0, data.end_num.max())

# Top ticks (markings)
xticks_top_minor = np.arange(0, data.end_num.max()+1, 7)
ax_top.set_xticks(xticks_top_minor, minor=True)
# Top ticks (label)
xticks_top_major = np.arange(3.5, data.end_num.max()+1, 7)
ax_top.set_xticks([])
# Week labels
xticks_top_labels = []
for week in range(1, len(xticks_top_minor)+1):
    xticks_top_labels.append(f"Week {week}\n"
                             f"{(project_start + (week - 1) * pd.Timedelta(days=7)).strftime('%d/%m/%y')}")
# xticks_top_labels.append([f"Week {i}"for i in np.arange(1, len(xticks_top_major)+1, 1)])
ax_top.set_xticklabels(xticks_top_labels, ha='left', minor=True)

# Grid lines
ax_top.set_axisbelow(True)
ax_top.xaxis.grid(color='gray', linestyle='dashed', alpha=0.3, which='both')

# Hide major tick (we only want the label)
ax_top.tick_params(which='major', color='w')
# Increase minor ticks (to marks the weeks start and end)
ax_top.tick_params(which='minor', length=8, color='k')

# Text
plt.text(-9.5, amount_of_tasks, "Task   Code  Resp. Hr.", fontdict=font, size=12)

# Show
fig.tight_layout()
plt.show()
