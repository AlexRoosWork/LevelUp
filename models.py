# File for everything related to the database to track progress

import datetime
import os
import sys
import shutil

from sqlalchemy import Column, String, Integer, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# setting up the engine for the database and some constants
BASE = os.path.dirname(sys.argv[0])
DATABASE = BASE + os.sep + "db/level.db"
engine = create_engine("sqlite:///" + DATABASE)
Session = sessionmaker(bind=engine)  # instantiate a session and connect it to our db
session = Session()

# instantiating the base for the models
Base = declarative_base()


def setup_database():
    """Create the directory for the database.
    Make sure the directory exists"""
    os.makedirs(BASE + os.sep + "db", exist_ok=True)


class Entry(Base):
    """Class for each entry in the database"""

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)  # will not be used further
    date = Column(Date, nullable=False)  # date of the entry
    minutes = Column(Integer)  # number of minutes on a given date
    skill = Column(
        ForeignKey("skills.name"), nullable=False
    )  # name of the skill improved

    @staticmethod
    def add_null_date(skillname):
        """Add days with no time spent in them, also activates every time a new entry is made"""
        # get the first date for a skill in the db
        start = (
            session.query(Entry)
            .filter_by(skill=skillname)
            .order_by(Entry.date.asc())
            .first()
        )
        # if there is a start, if not, just skip, because we don't need to add 0 days
        if start is not None:
            start = start.date
            stop = datetime.datetime.now()  # stopping today
            while start.strftime("%Y-%m-%d") != stop.strftime("%Y-%m-%d"):
                # add one day
                start = start + datetime.timedelta(days=1)
                # if there is no entry for that day
                if (
                    session.query(Entry).filter_by(date=start, skill=skillname).first()
                    is None
                ):
                    # add a new entry with 0 minutes in the skillname
                    new_entry = Entry(date=start, minutes=0, skill=skillname)
                    session.add(new_entry)
                    session.commit()

    @staticmethod
    def create_entry(skillname):
        """Supplementary table to the times_table. Keeps track of total hours invested, current level, next level"""
        minutes = minute_input()  # verify input

        # store query in variable for easy repetition
        query_obj = session.query(Entry).filter_by(
            skill=skillname, date=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        # get first obj from the query
        entry = query_obj.first()
        # for newly created skills
        if entry is None:
            # create a new entry with the input minutes
            entry = Entry(
                skill=skillname, date=datetime.datetime.now(), minutes=minutes
            )
            session.add(entry)
        else:
            # add the minutes to the existing entry (either 0 day or something in it)
            entry.minutes += minutes
        session.commit()  # save changes to the database

    @staticmethod
    def get_minutes_invested(skillname):
        """Return the number of minutes invested in a skill today"""
        minutes = (
            session.query(Entry.minutes)
            .filter_by(
                skill=skillname, date=datetime.datetime.now().strftime("%Y-%m-%d")
            )
            .first()[0]
        )

        return minutes

    @staticmethod
    def get_total_minutes(skillname):
        """Return the total number of minutes invested in a skill"""
        entries = session.query(Entry.minutes).filter_by(skill=skillname).all()
        total = 0
        for entry in entries:
            total += entry[0]  # add the minutes to the total
        # update the total minues in the skill table
        skill_obj = session.query(Skill).get(skillname)
        skill_obj.total_minutes = total  # update the total in the Skill model
        session.commit()  # save changes to the db
        return total  # return the total for main.py


class Skill(Base):
    """Class for each skill """

    __tablename__ = "skills"

    name = Column(String, primary_key=True, unique=True)  # name of the skill
    current_level = Column(Integer, default=0)  # the level of the user
    total_minutes = Column(Integer, default=0)  # total minutes invested
    xp_points = Column(Integer, default=0)  # xp points in current level
    daily_goal = Column(Integer, default=0)  # number of minutes to reach every day


def minute_input():
    """Verfiy the input of the user to only allow integers above 0"""
    while True:
        # only allow integers above 0 as input
        try:
            minutes = int(input("Enter MINUTES: "))
            if minutes >= 0:
                return minutes
            else:
                print("Enter an integer greater than 0.")
        except ValueError:
            print("Enter an integer.")


def set_goal(skillname):
    """Let the user change the goal setting for a skill"""
    skill_obj = session.query(Skill).get(
        skillname
    )  # get the skill from the Skill model
    minutes = minute_input()  # let the user input minutes
    skill_obj.daily_goal = minutes  # update the daily goal in Skill model
    session.commit()  # commit changes to database


def create_skill():
    """Add a new row (skill) in the level_table"""
    verification = 3  # base verification integer
    # once verification is above 3, all criterions are met
    while (
        verification < 4
    ):  # verification loop for new skillname, only create skill after all checks have passed
        verification = 3
        skillname = input("Name the skill: ").strip().lower().title()
        if " " in skillname:
            print("Sorry, skillnames cannot include a whitespace character.")
            verification -= 1
        if len(skillname) <= 3:
            print("Please enter a skillname longer than 3 characters.")
            verification -= 1
        if session.query(Skill).filter_by(name=skillname).first():
            print("This skill already exists!")
            verification -= 1
        else:
            verification += 1
    skill = Skill(name=skillname)  # add a new skill to the Skill model
    session.add(skill)
    session.commit()  # save changes to database


def get_skill_names():
    """Returns a list of all names for the skills in the level_table"""
    skill_names = [instance.name for instance in session.query(Skill)]
    return skill_names


def update_level(skillname):
    """
    Update the level.db after new minutes have been entered,
    to calculate current level as well as next level"""

    skill_obj = session.query(Skill).get(skillname)
    total_hours = skill_obj.total_minutes / 60  # convert minutes to hours
    # logic for the level up calculation
    next_level = 1
    current_level = 0
    # check if there was a levelup
    while total_hours >= (next_level ** 2):
        current_level = next_level
        total_hours -= next_level ** 2
        next_level += 1
    xp_points = round(total_hours, 2)
    # Update the DB
    skill_obj.xp_points = xp_points
    skill_obj.current_level = current_level
    xp_required = round((next_level ** 2) - xp_points, 1)
    session.commit()  # save changes to Skill model
    return (
        skill_obj.current_level,
        next_level,
        xp_points,
        xp_required,
        skill_obj.daily_goal,
    )  # return for main.py


def convert_datetime_objs(dates_list):
    """Convert a list of date strings YYYY-MM-DD to datetime objects. Return list of datetime objects"""
    datetime_list = []
    for date in dates_list:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        datetime_list.append(date_obj)
    return datetime_list


def get_dates_and_hours(skill_list):
    """Get a dictionary of skills with dates, hours and goal for the plots"""
    skills = {}
    for skillname in skill_list:
        dates_list = []
        hours_list = []
        skill_obj = session.query(Skill).get(skillname)
        dates = (
            session.query(Entry.date)
            .filter_by(skill=skillname)
            .order_by(Entry.date.asc())
            .all()
        )
        hours = (
            session.query(Entry.minutes)
            .filter_by(skill=skillname)
            .order_by(Entry.date.asc())
            .all()
        )
        for date in dates:
            dates_list.append(date[0])
        for hour in hours:
            hours_list.append(hour[0])

        skills[skillname] = {
            "dates": dates_list,
            "minutes": hours_list,
            "goal": skill_obj.daily_goal,
        }

    # return the dictionary with skill, dates and minutes
    return skills


def import_db():
    """import an existing db from json file
    Not used in the main programm, only for dev purposes"""
    import json

    with open("/home/alex/python/times.json") as json_file:
        json_file = json_file.read()
    jfile = json.loads(json_file)
    for entry in jfile:
        new_entry = Entry(
            date=datetime.datetime.strptime(entry["date"], "%Y-%m-%d"),
            minutes=entry["minutes"],
            skill=entry["skill"],
        )
        session.add(new_entry)
    session.commit()


def get_stats(skill_dict):
    """Return the necessary datapoints to show the stats"""
    skill_list = [k for k in skill_dict.keys()]

    stats_dict = {}
    for skillname in skill_list:
        # get all entries for a particular skill
        query = (
            session.query(Entry.minutes)
            .filter_by(skill=skillname)
            .order_by(Entry.date.desc())
            .all()
        )
        # if there are datapoints for 2 months or more
        if len(query) >= 60:
            stats_dict[skillname] = {
                "last_week": total_interval(query, 0, 7),
                "previous_week": total_interval(query, 7, 14),
                "total_goals_week": goal_met(skillname, query, 0, 7),
                "last_month": total_interval(query, 0, 30),
                "previous_month": total_interval(query, 30, 60),
                "total_goals_month": goal_met(skillname, query, 0, 30),
            }
        # if there are only datapoints for 2 weeks to 2 months
        elif len(query) >= 14:
            stats_dict[skillname] = {
                "last_week": total_interval(query, 0, 7),
                "previous_week": total_interval(query, 7, 14),
                "total_goals_week": goal_met(skillname, query, 0, 7),
                "last_month": None,
                "previous_month": None,
                "total_goals_month": None,
            }
        # if there are no datapoints at all
        else:
            stats_dict[skillname] = {
                "last_week": None,
                "previous_week": None,
                "total_goals_week": None,
                "last_month": None,
                "previous_month": None,
                "total_goals_month": None,
            }

        return stats_dict


def goal_met(skillname, entries, start, stop):
    """Check how many times the goal has been met in the time interval"""
    total = 0
    # get goal for the skill
    skill_obj = session.query(Skill).get(skillname)
    goal = skill_obj.daily_goal
    for entry in entries[start:stop]:
        if goal <= entry[0]:
            total += 1
    return total


def total_interval(entries, start, stop):
    """Return the total minutes for a given time range"""
    total = 0
    interval = [entry[0] for entry in entries[start:stop]]
    for i in interval:
        total += i
    return total


def delete_skill(skillname):
    """Delte the given skill in the Skill model and all entries from the Entry model"""
    skill_obj = session.query(Skill).filter_by(name=skillname)
    entry_query = session.query(Entry).filter_by(skill=skillname)
    skill_obj.delete(synchronize_session=False)  # delete skill from Skill model
    entry_query.delete(synchronize_session=False)  # delte entries from Entry model
    session.commit()  # save changes to the database
