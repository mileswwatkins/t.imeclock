import csv
from datetime import datetime, date, timedelta
from cStringIO import StringIO
from operator import itemgetter

from flask import Flask, Response, g, redirect, render_template, request,\
        url_for
from flask.ext.login import LoginManager, current_user, login_required,\
        login_user, logout_user
from sqlalchemy import distinct
from timezones.tz_utils import guess_timezone_by_ip

from config import app, lm
from database import session
from forms import RegisterForm, LoginForm, SwitchProjectForm, HistoryDateForm
from models import User, Project, Spell
from utility import duration_to_plain_english


@app.route("/")
def no_route():
    if current_user.is_authenticated():
        return redirect("/current")
    else:
        return redirect("/login")

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=True)
        return redirect("/")
    return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/current", methods=["POST", "GET"])
@login_required
def current():
    form = SwitchProjectForm()
    user_timezone = guess_timezone_by_ip(request.remote_addr)
    current_spell = Spell.query.\
            filter(Spell.end == None).\
            join(Project).join(User).filter(User.id == current_user.id).\
            first()

    # Generate a list of existing projects from which user can choose
    DEFAULT_CHOICE_NO_PROJECT = (0, "")
    form_choices = [DEFAULT_CHOICE_NO_PROJECT]
    if current_spell:
        for project in current_user.projects:
            # Remove current project from the set of choices
            if project != current_spell.project:
                form_choices.append((project.id, project.name))
    form.existing_project.choices = form_choices

    # If the user is currently working, they have an option to stop working
    if request.form.get("button") == "... or stop working":
        current_spell.end = datetime.now(user_timezone)
        # Add this project to the form selection drop-down
        form.existing_project.choices.append(
                (current_spell.project_id, current_spell.project.name))
        current_spell = None

    # Otherwise, the user can choose a new or existing project to work on
    elif form.validate_on_submit():
        # Close the current project, if one exists
        if current_spell:
            current_spell.end = datetime.now(user_timezone)
            form.existing_project.choices.append(
                    (current_spell.project_id, current_spell.project.name))

        # If the user wants to start on a new project, create it
        if form.new_project.data:
            current_project = Project(
                    user_id=current_user.id, 
                    name=form.new_project.data
                    )
            # Add this to the projects table
            session.add(current_project)
            session.flush()

        # Otherwise, identify the existing project the user selected
        else:
            current_project = Project.query.\
                    filter(Project.id == form.existing_project.data).\
                    first()
            # Remove this project from the form selection drop-down
            form.existing_project.choices.remove(
                    (current_project.id, current_project.name))

        # Create a new database record for that project name
        current_spell = Spell(
                project_id=current_project.id,
                start=datetime.now(user_timezone)
                )
        session.add(current_spell)

        session.commit()

    # Sort choices alphabetically by project name
    form.existing_project.choices.sort(key=itemgetter(1))

    return render_template(
            "current.html",
            form=form,
            current_spell=current_spell)

@app.route("/history", methods=["POST", "GET"])
@login_required
def history():
    form = HistoryDateForm()
    user_timezone = guess_timezone_by_ip(request.remote_addr)
    sorted_durations = []

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        durations = {}

        # If a user has worked at all, sum their durations by project
        for project in current_user.projects:
            durations[project.name] = timedelta(0)
            for spell in project.spells:
                # Make a special case for the currently-ongoing project
                if spell.end == None:
                    if start_date <= spell.start.date() <= \
                            datetime.now(user_timezone).date() <= end_date:
                        durations[project.name] += spell.duration
                else:
                    if start_date <= spell.start.date() <= \
                            spell.end.date() <= end_date:
                        durations[project.name] += spell.duration
            # Convert summed durations to plain English
            durations[project.name] = \
                    duration_to_plain_english(durations[project.name])

        # Sort output alphabetically by project name
        sorted_durations = sorted(durations.iteritems(), key=itemgetter(0))

    return render_template(
            "history.html",
            form=form,
            durations=sorted_durations)

# Serve a file containing all of the current user's data
@app.route("/user_complete_history.csv")
@login_required
def generate_csv():
    user_timezone = guess_timezone_by_ip(request.remote_addr)
    output = StringIO()
    writer = csv.writer(output)
    DATE_FORMAT = "%c"

    header_info = "All T.imeclock data for {0}, as of {1}".format(
            current_user.email,
            datetime.now(user_timezone).strftime(DATE_FORMAT)
            )
    writer.writerow([header_info, "", ""])
    writer.writerow(["", "", ""])
    COLUMNS = ["name", "start", "end"]
    writer.writerow(COLUMNS)
    for project in current_user.projects:
        for spell in project.spells:
            # Resolve issues with null end times, for ongoing spells
            end_time = ""
            if spell.end:
                end_time = spell.end.strftime(DATE_FORMAT)
            spell_row = [
                    project.name,
                    spell.start.strftime(DATE_FORMAT),
                    end_time
                    ]
            writer.writerow(spell_row)

    return Response(output.getvalue(), mimetype="txt/csv")

@app.route("/about")
def about():
    return render_template("about.html")

# Issue: remove this after main development, for security purposes
# For development purposes, view all tables in the database
@app.route("/view_all_tables")
def view_all_tables():
    return render_template("view_all_tables.html",
            users=User.query.all(),
            projects=Project.query.all(),
            spells=Spell.query.all())


if __name__ == "__main__":
    app.run()
