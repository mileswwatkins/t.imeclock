from contextlib import closing
from datetime import datetime, date, timedelta
from operator import itemgetter

from flask import Flask, render_template, redirect, url_for, g, request,\
        Response
from flask.ext.login import LoginManager, login_required, login_user,\
        logout_user, current_user
from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms.validators import Email, Length, EqualTo
from sqlalchemy import distinct
from sqlalchemy.sql import func

from database import session
from models import User, Project


# Set application constants, and create application
DATABASE = '/tmp/timeclock.db'
DEBUG = True
SECRET_KEY = 'qmTcssHWNArLzQP9LmBJq7Y4hvdfc4'

app = Flask(__name__)
app.config.from_object(__name__)

# Configure login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"

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


# Create a login form
class LoginForm(Form):
    email = TextField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=32)])

# Create a registration form
class RegisterForm(Form):
    email = TextField('Email',
            validators=[Email(message="A valid email address, please")])
    password = PasswordField('Password', validators=[
            Length(min=1, max=32, message="Maximum password length is 32"),
            EqualTo("confirm_password", message="Passwords must match")])
    confirm_password = PasswordField('Confirm Password', validators=[
            Length(min=1, max=32, message="Maximum password length is 32")])

# Create a new project form
class NewProjectForm(Form):
    existing_project = SelectField("Existing Project", coerce=int)
    new_project = TextField("New Project Name")

# Create a form to select start and end dates for the history view
class HistoryDateForm(Form):
    start_date = DateField("Work On or After This Date (yyyy-mm-dd format)",
            default=date(2014, 1, 1))
    end_date = DateField("Work On or Before This Date (yyyy-mm-dd format)",
            default=datetime.today() + timedelta(1))


@app.route('/')
def no_route():
    if current_user.is_authenticated():
        return redirect('/current')
    else:
        return redirect('/login')

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=True)
        return redirect('/user_list')
    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/current', methods=['POST', 'GET'])
@login_required
def current():
    form = NewProjectForm()
    current_project = Project.query.\
            filter(Project.user_id == current_user.id).\
            filter(Project.start != None).\
            filter(Project.end == None).\
            first()

    # Generate a list of existing projects from which user can choose
    DEFAULT_CHOICE_NO_PROJECT = (-1, "")
    # Issue: allow user to take a break, not working on any project
    # Issue: allow user to stop working for the day
    form_choices = [DEFAULT_CHOICE_NO_PROJECT]
    if current_project:
        existing_projects = Project.query.\
                filter(Project.user_id == current_user.id).\
                filter(Project.name != current_project.name).\
                group_by(Project.id).order_by(Project.name)
        for project in existing_projects:
            form_choices.append((project.id, project.name))
    form.existing_project.choices = form_choices

    if form.validate_on_submit():
        # Close the current project, if one exists
        if current_project:
            current_project.end = datetime.now()
            current_project.duration = \
                    current_project.end - current_project.start
            # Add it to the form selection drop-down
            form.existing_project.choices.append(
                    (current_project.id, current_project.name))

        # If user selected an existing project, retrieve that project's name
        if form.existing_project.data != DEFAULT_CHOICE_NO_PROJECT[0]:
            project_name = Project.query.\
                    filter(Project.user_id == current_user.id).\
                    filter(Project.id == form.existing_project.data).\
                    first().name
            # Remove this project from the form selection drop-down
            form.existing_project.choices.remove(
                    (form.existing_project.data,
                    project_name))
        # If the user wants to start on a new project, use that name instead
        # Issue: need to forbid user from using one of their existing names
        else:
            project_name = form.new_project.data
        # Issue: deal with both select and new project fields being left blank

        # Create a new database record for that project name
        current_project = Project(name=project_name, user_id=current_user.id)
        current_project.start = datetime.now()
        session.add(current_project)
        session.commit()

    return render_template(
            'current.html',
            form=form,
            current_project=current_project)

@app.route('/history', methods=['POST', 'GET'])
@login_required
def history():
    form = HistoryDateForm()

    # Need to add timedelta(1) so that the end is the very close of the day
    # This is functionally equivalent to the very first moment of the next day
    start_date = form.start_date.data
    end_date = form.end_date.data + timedelta(1)

    # Issue: this query does not include the currently ongoing project
    projects=session.query(Project.name,
            func.sum(Project.duration)).\
            filter(Project.user_id == current_user.id).\
            filter(Project.start >= start_date).\
            filter(Project.end <= end_date).\
            group_by(Project.name).all()

    # Convert summed durations to plain English
    durations = []
    for project in projects:
        name = project[0]
        duration = project[1]

        duration_mins, duration_secs = divmod(duration.seconds, 60)
        duration_hours, duration_mins = divmod(duration_mins, 60)
        duration_text = ""
        if duration.days > 0:
            duration_text += str(duration.days) + " days, "
        if duration_hours > 0:
            duration_text += str(duration_hours) + " hours, "

        duration_text += str(duration_mins) + " minutes"
        durations.append((name, duration_text))

    # Sort output alphabetically by project name
    durations_sorted = sorted(durations, key=itemgetter(0))

    # Issue: add button to allow user to download their whole history

    return render_template(
            'history.html',
            form=form,
            durations=durations_sorted)

# Return a file containing all of the current user's data
@app.route('/download.csv')
@login_required
def generate_csv():
    def generate():
        columns = ["name", "start", "end"]
        field ",".join(columns) + "\n"
        projects=session.query(Project.name, Project.start, Project.end).\
                filter(Project.user_id == current_user.id)\
                .all()
        for project in projects:
            yield ",".join(project) + "\n"
    return Response(generate(), mimetype='txt/csv')

@app.route('/about')
def about():
    return render_template('about.html')

# For development purposes, print a list of all users and their passwords
@app.route('/user_list')
def user_list():
    return render_template('user_list.html', users=User.query.all())

# For development purposes, print a list of all the projects of a user
@app.route('/project_list')
@login_required
def project_list():
    return render_template(
            'project_list.html',
            current_user=current_user,
            projects=Project.query.filter(Project.user_id == current_user.id))

if __name__ == '__main__':
    app.run()
