#!/usr/bin/env python3
import shutil


def print_progressbar(
    iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percentage = iteration / float(total) * 100
    percent = ("{0:." + str(decimals) + "f}").format(percentage)
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    # print the progress bar
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    # Print New Line on Level Complete instead of a progress bar
    if iteration == total:
        print()


def output_summary(
    skillname,
    current_level,
    next_level,
    xp_points,
    xp_required,
    total_hours,
    minutes_invested,
    goal=None,
):
    """Print output to the user after they have entered some data"""
    terminal_length = shutil.get_terminal_size()[0]  # fit to the length of the termial
    # actual output
    print(
        f"\n{'~' * ((terminal_length - 8) // 2)}LEVEL UP{'~' * ((terminal_length - 8) // 2)}\n"
    )
    print(f"{skillname} level: {current_level}".center(terminal_length))
    print(f"Time invested today: {minutes_invested} minutes".center(terminal_length))
    print(f"Total time invested: {round(total_hours, 1)} hours".center(terminal_length))
    if goal:
        print()
        if goal <= minutes_invested:
            print("You have reached your daily goal!".center(terminal_length))
        else:
            print(
                f"{minutes_invested - goal} minutes to reach your daily goal".center(
                    terminal_length
                )
            )
    print()
    print(
        f"To reach level {next_level} you need to spend {xp_required} more hours.".center(
            terminal_length
        )
    )
    print()
    print_progressbar(
        iteration=xp_points,
        total=(next_level ** 2),
        suffix=f"to Level {str(next_level)}",
        length=(terminal_length - len(str(next_level)) - 20),
    )
    print()
    print(
        f"{'~' * ((terminal_length - 40) // 2)}STUMBLE FORWARD INTO THE KINGDOM OF GOD!{'~' * ((terminal_length - 40) // 2)}"
    )
    print("\n\n")


def show_stats(stats_dict):
    """Show some stats for the progress"""
    # query the db for either all entries or only a specific skill
    string = ""
    terminal_length = shutil.get_terminal_size()[0]  # fit output to terminal size
    for key, value in stats_dict.items():
        string += f"\n{'=' * ((terminal_length - (len(key) + 10)) // 2)}STATS FOR {key.upper()}{'=' * ((terminal_length - (len(key) + 10)) // 2)}\n"
        # weekly stats
        if value["last_week"]:
            last_week = value["last_week"]
            previous_week = value["previous_week"]
            total_goals_week = value["total_goals_week"]
            delta_week = last_week - previous_week
            average_7_days = round(last_week / 7)
            string += "\n"
            string += "WEEKLY STATS".center(terminal_length)
            string += f"""
Total minutes this week: {last_week} min
Compared to last week: {delta_week} min ({calc_percentage(last_week, previous_week)})
Average per day: {average_7_days} min
Daily Goal reached: {total_goals_week} times
"""
        else:
            string += "\nNot enough data weekly stats"
        # monthly stats
        if value["last_month"]:
            last_month = value["last_month"]
            previous_month = value["previous_month"]
            total_goals_month = value["total_goals_month"]
            delta_month = last_month - previous_month
            average_month = round(last_month / 30)
            string += "\n"
            string += "MONTHLY STATS".center(terminal_length)
            string += f"""
Total minutes this month: {last_month} min
Compared to last month: {delta_month} min ({calc_percentage(last_month, previous_month)})
Average per day: {average_month} min
Daily goal reached: {total_goals_month} times

Average minutes per day last week compared to last month: {average_7_days - average_month} min ({calc_percentage(average_7_days, average_month)})
"""
        else:
            string += "\nNot enough data to show monthly stats"
        string += f"\n{'=' * terminal_length}\n"
    return string


def lvlup_help():
    """Give the user information about the program and how to use it"""
    terminal_length = shutil.get_terminal_size()[0]  # fit to terminal size
    # actual output
    print(
        f"\n{'~' * ((terminal_length - 12) // 2)} HOW TO USE {'~' * ((terminal_length - 12) // 2)}\n"
    )
    print("LevelUp is a simple python program to gamify your learning process!\n\n")
    print(
        "To reach a given level N, you have to invest N ** 2 hours. So, 1 hour for level 1, 4 hours for level 2, 9 hours for level 3 and so on."
    )
    print(
        "During your working time best keep track with a stopwatch and then enter the completed minutes in the programm.\n"
    )
    print(
        "Level Up can also show you graphs about recent progress and all time progress.\n\n"
    )
    print(
        "The project is open source and available on GitLab ( https://gitlab.com/AlexAnarcho/levelup/ ). Feel free to improve it to your liking :)\n\n"
    )
    print(
        f"\n{'~' * ((terminal_length - 12) // 2)} HOW TO USE {'~' * ((terminal_length - 12) // 2)}\n"
    )
    input("Press any key to continue...")


def calc_percentage(num1, num2):
    """Calculate the appropriate percentage and return a string for show_stats"""
    base = num1 / num2 * 100
    base = round(base)
    if base >= 100:
        percent = base - 100
        string = f"{percent}% more"
    elif base < 100:
        percent = 100 - base
        string = f"{percent}% less"
    return string
