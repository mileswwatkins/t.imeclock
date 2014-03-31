from datetime import datetime, date, timedelta
from operator import itemgetter

from flask import Flask, Response, g, redirect, render_template, request,\
        url_for
from flask.ext.login import LoginManager, current_user, login_required,\
        login_user, logout_user
from flask.ext.mail import Mail, Message
from sqlalchemy import distinct

from database import session
from models import User, Project, Spell
from forms import RegisterForm, LoginForm, SwitchProjectForm, HistoryDateForm


# Set application constants, and create application
DATABASE = "/tmp/timeclock.db"
# Issue: after development this DEBUG needs to get turned off, for security
DEBUG = True
SECRET_KEY = "qmTcssHWNArLzQP9LmBJq7Y4hvdfc4"

app = Flask(__name__)
app.config.from_object(__name__)

# Configure login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"

# Configure mail manager
mail = Mail(app)

# Remove the database session at the end of a request or at shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

# Allow login manager to load a user from the database
@lm.user_loader
def load_user(id):
    if id is not None:
        return User.query.get(int(id))
    else:
        return None

# Remember the current user
@app.before_request
def before_request():
    g.user = current_user

# Utility function to convert duration objects into human-readable form
def duration_to_plain_english(duration):
    duration_mins, duration_secs = divmod(duration.seconds, 60)
    duration_hours, duration_mins = divmod(duration_mins, 60)

    duration_text = ""

    if duration.days > 0:
        if duration.days == 1:
            duration_text += "1 day, "
        else:
            duration_text += str(duration.days) + " days, "

    if duration_hours > 0:
        if duration_hours == 1:
            duration_text += "1 hour, "
        else:
            duration_text += str(duration_hours) + " hours, "

    if duration_mins == 1:
        duration_text += "1 minute"
    else:
        duration_text += str(duration_mins) + " minutes"

    return duration_text


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

        activation_code = user.password[-15:]
        email_account_confirmation = Message(
                subject="Confirm Your T.imeclock Account",
                body="Please confirm your account by clicking on this link:" +\
                activation_link,
                sender=("T.imeclock Admin", "miles.w.watkins@gmail.com"),
                recipients=[form.email.data])
        mail.send(email_account_confirmation)

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
        current_spell.end = datetime.now()
        # Add this project to the form selection drop-down
        form.existing_project.choices.append(
                (current_spell.project_id, current_spell.project.name))
        current_spell = None

    # Otherwise, the user can choose a new or existing project to work on
    elif form.validate_on_submit():
        # Close the current project, if one exists
        if current_spell:
            current_spell.end = datetime.now()
            form.existing_project.choices.append(
                    (current_spell.project_id, current_spell.project.name))

        # If the user wants to start on a new project, create it
        if form.new_project.data:
            current_project = Project(
                    user_id=current_user.id, 
                    name=form.new_project.data)
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
        current_spell = Spell(project_id=current_project.id)
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
                            date.today() <= end_date:
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

# Issue: view appears to be broken, and only exports the header row
# Return a file containing all of the current user's data
@app.route("/user_complete_history.csv")
@login_required
def generate_csv():
    COLUMNS = ["name", "start", "end"]
    def generate():
        yield ",".join(COLUMNS) + "\n"
        for project in current_user.projects:
            for spell in project.spells:
                attributes = []
                attributes.append(spell.project.name)
                attributes.append(str(spell.start))
                attributes.append(str(spell.end))
                yield ",".join(attributes) + "\n"
    return Response(generate(), mimetype="txt/csv")

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
