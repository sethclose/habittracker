import datetime
import uuid
#from flask import Blueprint, request, redirect, url_for, render_template, current_app
import flask

# This is imported into app.py
# All routes in html use url_for now need the name below appended:  habits.index, for example
pages = flask.Blueprint("habits", __name__, template_folder="templates", static_folder="static")

@pages.context_processor                # Adds date_range to every template (jinja mastery)
def add_calc_date_range():              #   This name could be anything, it seems
    def date_range(start: datetime.datetime):  # This is used in layout.html main dates
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}   # Adds this to every template (jinja mastery)
                                        # Replaces date_range=date_range as passed render_template kwarg
# Use this instead of Today() to get a 00 00 00 date time that can be used like a date
def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

# Main Page, defaults date if necessary, gets all habits created on or before selected date
#  Then gets habit ids for all habits completed on selected date
@pages.route("/")
def index():
    date_str = flask.request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()
    habits_on_date = flask.current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [         # habitIds completed from selected date
        completion["habit"] # habitId
        for completion      # instance in completions
        in flask.current_app.db.completions.find({"date": selected_date})
    ]

    return flask.render_template(
        "index.html",
        habits=habits_on_date,
        selected_date=selected_date,
        completions=completions,
        title="Habit Tracker - Home",
    )

@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if flask.request.form:
        flask.current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex,  # no explanation of this, just use this, I guess?
             "added": today,
             "name": flask.request.form.get("habit")}  # "habit" is the name, not id, which is used for label, css, etc
        )

    return flask.render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today
    )

@pages.route("/complete", methods=["POST"])
def complete():
    date_string = flask.request.form.get("date")  # id = date in
    date = datetime.datetime.fromisoformat(date_string)
    habit = flask.request.form.get("habitId")
    flask.current_app.db.completions.insert_one(
        {"date": date,
         "habit": habit}
    )

    return flask.redirect(flask.url_for(".index", date=date_string))
