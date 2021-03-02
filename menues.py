# This file gives the menues and does the appropriate actions for the selections
# Some other functions are included to reduce clutter and imports

import datetime
import os
import shutil
import inquirer

# import from other self-made modules
from graphs import *
from models import (
    get_dates_and_hours,
    get_skill_names,
    create_skill,
    set_goal,
    get_stats,
    delete_skill,
    BASE,
    DATABASE,
)
from output import lvlup_help, show_stats


def main_menu():
    """
    Provide main navigation options. Runs in an infinite loop, until exited"""
    clear_screen()  # clear screen before displaying option
    # list with all possible menu options
    menu_options = ["Improve Skill", "Insights", "Settings", "Exit"]
    # inquirer to display the menu
    menu = [
        inquirer.List(
            "main_menu",
            message="What do you want to do?",
            choices=menu_options,
            carousel=True,
            default="Improve Skill",
        ),
    ]
    # get the choice from the menu as a string
    choice = inquirer.prompt(menu)["main_menu"]
    # logic for selections, compared with menu_options
    if choice == menu_options[0]:
        skill = skill_menu()  # return the skill
        return skill  # breaks out of loop, further actions in main.py
    elif choice == menu_options[1]:
        insight_menu()  # call the insight menu
    elif choice == menu_options[2]:
        settings_menu()  # call the settings menu
    elif choice == menu_options[3]:
        print("Goodbye! See you soon.")
        exit()  # break out of the programs


def skill_menu():
    """Let the user pick a skill to improve.
    Used as a submenu for verious actions."""
    clear_screen()  # start with a fresh screen
    # get skills from the Skill model
    menu_options = [skill for skill in get_skill_names()]
    menu_options.append("Go Back")  # include the option to get back
    # inquirer logic
    menu = [
        inquirer.List(
            "skill_menu", message="Pick a skill", choices=menu_options, carousel=True,
        ),
    ]
    # store selection in string
    choice = inquirer.prompt(menu)["skill_menu"]
    if choice == menu_options[-1]:
        main_menu()  # if go back, call main_menu
    else:
        return choice  # return the skill choice for next action


def settings_menu():
    """Let the user choose a setting"""
    clear_screen()  # start with fresh screen
    # all options implemented
    menu_options = [
        "Add a new skill",
        "Delete a skill",
        "Set a daily goal",
        "Create backup",
        "Display Help",
        "Go Back",
    ]
    # inquirer logic
    menu = [
        inquirer.List(
            "settings_menu",
            message="Chose your setting",
            choices=menu_options,
            carousel=True,
        ),
    ]
    choice = inquirer.prompt(menu)["settings_menu"]
    if choice == menu_options[0]:
        # Add a new skill
        create_skill()  # call function to create a new skill
    elif choice == menu_options[1]:
        # delete a skill
        skillname = skill_menu()  # get the skill from skill_menu
        # confirmation to delete the skill
        key = input(f"Are you 100% sure you want to delete {skillname}? [y/N] ")
        if key.lower() == "y":
            delete_skill(skillname)  # actually delete the skill
            # give user feedback
            input(f"Deleted {skillname}\nPress ENTER to continue...")
    elif choice == menu_options[2]:
        # Set a daily goal for a skill
        skillname = skill_menu()  # choose the skill
        print("\nHow many minutes do you plan on investing per day?")
        set_goal(skillname)  # call function to set goal in Skill model
    elif choice == menu_options[3]:
        # create a backup
        file_path = backup_db()  # create backup and return filepath
        # give user feedback, let them know where the backup is
        print(f"Backup successfully created at {file_path}")
        input("Press ENTER to continue...")
    elif choice == menu_options[4]:
        # display the help string
        lvlup_help()
    elif choice == menu_options[-1]:
        # go back to main menu
        main_menu()


def insight_menu():
    """Let the user select the skills to get insights for"""
    clear_screen()  # start with a fresh screen
    # two menues, first select a skill, then the kind of insight to display
    menu_options_1 = [skill for skill in get_skill_names()]
    menu_options_2 = [
        "Stats",
        "Graph: All Time",
        "Graph: Past Month",
        "Graph: Past Week",
    ]
    menu = [
        # checkbox allows for multiple selections
        inquirer.Checkbox(
            "skills",
            message="Pick your skills by pressing the SPACE BAR",
            choices=menu_options_1,
        ),
        inquirer.List(
            "insights",
            message="Pick what insight to display",
            choices=menu_options_2,
            carousel=True,
        ),
    ]
    # prompt the menu
    choices = inquirer.prompt(menu)
    # selected skills
    skill_list = choices["skills"]
    # kind of insight to display
    insight = choices["insights"]
    # make sure something is selected
    if len(skill_list) == 0:
        print(
            "\n\nERROR:\nOh no! Looks like you didn't pick a skill!\nPick at least one skill!"
        )
        input("Press ENTER to continue...")
        insight_menu()
    else:
        # call appropriate insight
        skills_dict = get_dates_and_hours(skill_list)  # get data for selection
        if insight == menu_options_2[0]:
            clear_screen()
            print(show_stats(get_stats(skills_dict)))
            input("Press ENTER to continue...")
        elif insight == menu_options_2[1]:
            # all time progress
            plot_cumulated_progress(skills_dict, start=0)
        elif insight == menu_options_2[2]:
            # monthly time investment
            plot_minutes(skills_dict, start=-30)
        elif insight == menu_options_2[3]:
            # weekly time investment
            plot_minutes(skills_dict, start=-7)


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def backup_db():
    """Create a backup of the database"""
    # contruct filepath and name for backup
    new_backup = (
        BASE
        + os.sep
        + "db"
        + os.sep
        + "backup-"
        + datetime.datetime.now().strftime("%Y-%m-%d")
        + ".db"
    )
    # copy the existing database to new filename
    shutil.copy2(
        DATABASE, new_backup,
    )
    return new_backup
