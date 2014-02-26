from flask import Flask, render_template, redirect, url_for, g, request

from flask.ext.login import LoginManager, login_required, login_user,\
        logout_user, current_user

from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms.validators import Email, Length, EqualTo

from contextlib import closing

from sqlalchemy import distinct
from sqlalchemy.sql import func

from datetime import datetime, date, timedelta

from database import session
from models import User, Project


# Set application constants, and create application
DATABASE = '/tmp/timeclock.db'
DEBUG = True
SECRET_KEY = 'whateverrrr'

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
    form_choices = [DEFAULT_CHOICE_NO_PROJECT]
    existing_projects = Project.query.\
            filter(Project.user_id == current_user.id).\
            filter(Project.name != current_project.name).\
            group_by(Project.name).order_by("name")
    for project in existing_projects:
        form_choices.append((project.id, project.name))
    form.existing_project.choices = form_choices

    if form.validate_on_submit():
        # Close the current project, if one exists
        if current_project:
            current_project.end = datetime.now()

        # If user selected an existing project, retrieve that project's name
        if form.existing_project.data != DEFAULT_CHOICE_NO_PROJECT[0]:
            project_name = Project.query.\
                    filter(Project.user_id == current_user.id).\
                    filter(Project.id == form.existing_project.data).\
                    first().name
        # If the user wants to start on a new project, use that name instead
        else:
            project_name = form.new_project.data
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

    start_date = datetime.now().date()
    # Need to add timedelta(1) so that the end is the very close of the day
    # This is functionally the same as the very first moment of the next day
    end_date = datetime.now().date() + timedelta(1)
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data + timedelta(1)

    return render_template(
            'history.html',
            form=form,
            projects=session.query(Project.name, Project.duration).\
                    filter(Project.user_id == current_user.id).\
                    filter(Project.start >= start_date).\
                    filter(Project.end <= end_date).\
                    all())

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
