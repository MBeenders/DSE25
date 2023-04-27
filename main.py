import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime


data = pd.read_csv("files/file_04.csv", parse_dates=['Started', 'Due'], dayfirst=True)
print(data.columns)

font = {'family': 'monospace',
        'color': 'black',
        'weight': 'normal',
        'size': 7}


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
max_indent = 4
for row in description_data:
    indent = row[1].count('.')
    task = f'{row[1].strip()}. {row[0]}'
    changed = f'{" " * indent}{task:<40}{" " * (max_indent - indent)}{row[2]:>5}{row[3]:>5}'
    descriptions.append(changed)

data["Description"] = descriptions
amount_of_tasks = len(data["Task"].tolist())

add_colour(data)

weights = [100**4, 100**3, 100**2, 100, 1]
data = data.sort_values("Code", key=lambda ser: ser.apply(lambda x: -sum([weights[idx] * int(val) for idx, val in enumerate(x.split("."))])), ignore_index=True)
# data = data.sort_values(["Code"], ascending=[False])

# Add row number to description
max_index = len(data.index)
descriptions = []
for index, row in data.iterrows():
    descriptions.append(f'{max_index - index:<4} {row[17]}')
data['Description'] = descriptions

# create title row
# title_row = pd.DataFrame(0, index=pd.RangeIndex(len(data) + 1), columns=data.columns)
# title_row['Description'] = ' ' * 5 + 'Task' + ' ' * 40 + 'Pers. Time'
# title_row['colour'] = '#F8CECC'
# data = pd.concat([data.loc[:], title_row]).reset_index(drop=True)

fig, ax1 = plt.subplots(1, figsize=(11.7, 16.5 * 1.5))

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
    tick.set_fontname("monospace")
for tick in ax1.get_yticklabels():
    tick.set_fontname("monospace")

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
ax_top.set_xticklabels(xticks_top_labels, rotation=0, ha='left', minor=True)

# Grid lines
ax_top.set_axisbelow(True)
ax_top.xaxis.grid(color='gray', linestyle='dashed', alpha=0.3, which='minor')
ax_top.xaxis.grid(which='major', color='k', linestyle='dashed', alpha=0.3)

# Set tick lengths and color equal for major and minor ticks
ax_top.tick_params(which='major', color='k', length=2)
ax_top.tick_params(which='minor', length=2, color='k')

# Minor ticks each day, major ticks each week
minor_ticks = [x for x in range(0, 9 * 7 + 6) if x %7 != 0]
minor_labels = ['T', 'W', 'T', 'F', 'S', 'S'] * 9 + ['T', 'W', 'T', 'F', '']
major_ticks = list(range(0, 9 * 7 + 5, 7))
major_labels = ['M'] * 10
ax_top.set_xticks(minor_ticks, minor=True, labels=minor_labels, fontsize=6, ha='left')
ax_top.set_xticks(major_ticks, labels=major_labels, fontsize=6, ha='left')
ax_top.tick_params(axis='x', which='major', pad=0)
ax_top.tick_params(axis='x', which='minor', pad=0)

# Add "Week i" labels
n = 7 * 9 + 5
for i in range(9):
    x = 1 / n * (7 * i + 3.5)
    ax_top.text(x, 1.008, f'Week {i + 1}', transform=ax_top.transAxes, fontsize=9, ha='center')
ax_top.text(1 / n * (7 * 9 + 2.5), 1.008, 'Week 10', transform=ax_top.transAxes, ha='center', fontsize=9)

# Add column names
ax_top.text(-0.205, 1.002, 'Task', transform=ax_top.transAxes, fontsize=6)
ax_top.text(-0.06, 1.002, 'Person', transform=ax_top.transAxes, fontsize=6)
ax_top.text(-0.025, 1.002, 'Time', transform=ax_top.transAxes, fontsize=6)

# Color top-level tasks
for tl in ax1.get_yticklabels():
    tl.set(fontsize=4)
    tl.set_linespacing(1.0)
    txt = tl.get_text()
    if txt[6:8] == '. ':
        txt += ' (!)'
        tl.set_backgroundcolor('#DAE8FC')
    elif txt[9:11] == '. ':
        txt += ' (!)'
        tl.set_backgroundcolor('#E1D5E7')
    tl.set_text(txt)

# Text
# plt.text(-40, amount_of_tasks, f"{'Code':<10} {'Task':<27}{'Resp.':<5} {'Hr.':<5}", fontdict=font, size=12)


n = len(data.index)
ax1.set_ylim(-0.5, n - 0.5)

# Show
fig.tight_layout()
plt.savefig('test.pdf')
# plt.show()
