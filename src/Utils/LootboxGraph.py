import logging
import sys
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.container import BarContainer

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Database import Database
from Database.attributes import ATTR_LUCK
from Utils.utils import DAILY, WEEKLY, MONTHLY, STREAK
from commands import lootboxes as LB


def get_graph(user_id) -> tuple[str, Figure]:
    # Add values on top of bars
    def label_bars(bars: BarContainer, ax: Axes):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f'{height:.2f}', ha='center', va='bottom', color='#ffffff')

    # user_time_data = Database.get_claim_timestamps(202112441457442816)
    user_time_data = Database.get_claim_timestamps(user_id)
    user_atts = Database.get_user_attributes(user_id)

    # Get the weights per each claim type
    BASE = "base"
    weights = {}
    types = [BASE, DAILY, WEEKLY, MONTHLY]
    next_streaks = {
        BASE: 0,
        DAILY: user_time_data[DAILY][STREAK] + 1,
        WEEKLY: user_time_data[WEEKLY][STREAK] + 1,
        MONTHLY: user_time_data[MONTHLY][STREAK] + 1,
    }
    for type in types:
        if type == BASE:
            (_, weights[type]) = LB.roll_lootbox_tier(DAILY, 0, user_atts)
        else:
            (_, weights[type]) = LB.roll_lootbox_tier(type, next_streaks[type], user_atts)

    # Calculate percentages from weights
    percentages = {
        BASE: [],
        DAILY: [],
        WEEKLY: [],
        MONTHLY: [],
    }
    for type in types:
        total = sum(list(weights[type].values()))
        for v in list(weights[type].values()):
            percentages[type].append(v/total*100)

    x_labels = list(weights[DAILY].keys())  # all keys/labels are the same
    x = np.arange(len(x_labels))  # Numeric x locations for the groups
    num_sets = len(types)
    bar_width = 0.9 / num_sets

    # Create the Figure
    figure = Figure(figsize=(12, 5), dpi=90, tight_layout=True, facecolor='#1e1e1e')  # light gray
    percent_plot = figure.add_subplot(111)
    percent_plot.set_facecolor('#2a2a2a')
    percent_plot.clear()
    # Plot each dataset with an offset
    for i, type in enumerate(percentages):
        offset = (i - (num_sets - 1) / 2) * bar_width
        if type == BASE:
            bars = percent_plot.bar(x + offset, percentages[type], width=bar_width, label='Base Chance')
        else:
            bars = percent_plot.bar(x + offset, percentages[type], width=bar_width, label=f'{type.title()} Streak {next_streaks[type]}')
        label_bars(bars, percent_plot)

    # Add labels and legend
    percent_plot.set_xlabel("Rarity", color='#ffffff')
    percent_plot.set_ylabel("Percent", color='#ffffff')
    percent_plot.set_title(f"Next Claim Chances ({user_atts[ATTR_LUCK]} Luck)", color='#ffffff')
    percent_plot.set_xticks(x)
    percent_plot.set_xticklabels(x_labels, color='#ffffff')
    percent_plot.legend()
    percent_plot.tick_params(colors='#ffffff')
    for spine in percent_plot.spines.values():
        spine.set_color('#ffffff')

    # scale the Y-Axis of the graph
    b_max = max(percentages[BASE])
    d_max = max(percentages[DAILY])
    w_max = max(percentages[WEEKLY])
    m_max = max(percentages[MONTHLY])
    ymax = max(b_max, d_max, w_max, m_max, 30)
    percent_plot.set_ylim(0, ymax+3)

    name = f"u{user_id}_L{user_atts[ATTR_LUCK]}_D{next_streaks[DAILY]}_W{next_streaks[WEEKLY]}_M{next_streaks[MONTHLY]}"
    return (name, figure)


if __name__ == "__main__":
    file = os.path.abspath(os.path.normpath("./testing_data.db"))
    logger = logging.getLogger('discord')
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    Database.init_db(file, logger)
    name, fig = get_graph(202112441457442816)
    try:
        fig.savefig(f"{name}.png", dpi=300, bbox_inches='tight')
    except Exception as e:
        print(f"Failed to save graph: {e}")
