# File that ties all the other functions and models together
# Runs the main programm

import datetime
import shutil
from sqlalchemy import create_engine

# import everything that is needed from selfmade modules
from models import *
from menues import main_menu
from output import output_summary, show_stats


os.makedirs(BASE + os.sep + "db", exist_ok=True)
Base.metadata.create_all(engine)


def main():
    """Main programm - ties the database together with the frontend for the user"""
    while True:
        # main loop
        skill_choice = None
        while skill_choice is None:
            # main menu_loop
            skill_choice = main_menu()
        entry = Entry()  # instantiate a new entry
        entry.add_null_date(skill_choice)  # fill in 0 days
        entry.create_entry(skill_choice)  # create a new entry with minutes
        # get total minutes invested in skill today
        minutes_invested = entry.get_minutes_invested(skill_choice)
        # get hours in total in the skill
        total_hours = round(entry.get_total_minutes(skill_choice) / 60, 2)
        # update the level of the skill
        current_level, next_level, xp_points, xp_required, goal = update_level(
            skillname=skill_choice
        )
        # give main output for the user
        output_summary(
            skillname=skill_choice,
            current_level=current_level,
            next_level=next_level,
            xp_points=xp_points,
            xp_required=xp_required,
            minutes_invested=minutes_invested,
            total_hours=total_hours,
            goal=goal,
        )
        input("\n\nPress ENTER to continue...")


if __name__ == "__main__":
    # import_db()
    main()
