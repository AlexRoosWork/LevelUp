# call matplotlib with the data of the learning progress
# all graphs are show in XKCD style

import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates


def add_hours(minutes_list):
    """Take a list of minutes and convert it into cumulative list of hours"""
    hours_progress = []  # instantiate an empty list
    total = 0  # total starts at 0
    for minutes in minutes_list:
        total += minutes / 60  # convert minutes to hours and add to total
        hours_progress.append(total)  # add new total to the list
    return hours_progress  # return list of totals


def plot_cumulated_progress(skills, start):
    """Plot the cumulated progress in the given skills"""
    # basic plot setup
    plt.xkcd()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # go through every key (skill) in the dict and plot it's stats
    for key, value in skills.items():
        # plot the goal line
        goal_list = [value["goal"] for i in range(len(value["dates"]))]
        accumulated_goal = add_hours(goal_list)  #
        ax.plot(
            value["dates"],
            accumulated_goal,
            linestyle="dotted",
            label=f"Goal line for {key}",
        )
        # plot the cumulated progress line with hours added up
        hours_progress = add_hours(value["minutes"][start:])
        ax.plot(value["dates"], hours_progress, linestyle="solid", label=key)
        ax.set_ylim(bottom=0)  # let the y axis start at 0
        # customise plot title if one or more skills were selected
        if len(skills) < 2:
            plt.title(f"All time progress for {key}")
        else:
            plt.title("Progress over all time")
    # more basic setup
    plt.gcf().autofmt_xdate()
    date_format = mpl_dates.DateFormatter("%d.%m")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.legend(loc=2)
    plt.ylabel("Total hours invested")
    plt.grid(True)
    plt.tight_layout()
    # show the graph
    plt.show()


def plot_minutes(skills, start):
    """Plot minutes per day in time range"""
    # basic plot setup
    plt.xkcd()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # loop through skills and plot their lines
    for key, value in skills.items():
        latest_date_strings = value["dates"][start:]
        daily_goal = value["goal"]
        # if it exists, plot the daily_goal line
        if daily_goal > 0:
            daily_goal_list = [daily_goal for i in range(len(latest_date_strings))]
            ax.plot(
                latest_date_strings,
                daily_goal_list,
                linestyle="dotted",
                label=f"Daily Goal for {key}",
            )
        # plot the invested minutes line
        latest_hours = value["minutes"][start:]
        ax.plot(latest_date_strings, latest_hours, linestyle="solid", label=key)
        # basic y axis setup
        ax.set_ylim(bottom=0, top=(max(latest_hours) + 110))
        # customize the plot title
        if len(skills) < 2:
            plt.title(f"Minues per day for {key}")
        else:
            plt.title("Minutes per day")
    # more basic setup
    plt.legend(loc=2)
    plt.gcf().autofmt_xdate()
    date_format = mpl_dates.DateFormatter("%d.%m")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.ylabel("Minutes")
    plt.grid(True)
    plt.tight_layout()
    # show the graph
    plt.show()
