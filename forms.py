from datetime import datetime, date, timedelta

from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms.validators import Email, Length, EqualTo


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
