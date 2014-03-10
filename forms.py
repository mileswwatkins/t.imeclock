from datetime import datetime, date
import re

from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms.validators import Email, Length, EqualTo, Required,\
        ValidationError

from database import session
from models import User, Project


# Validator to determine whether a date is in WTForms-compatible format
def date_validator(form, field):
    date_checker = re.compile('\d{4}\-\d{2}-\d{2}')
    if not date_checker.match(field.data):
        raise ValidationError("Date must be in yyyy-mm-dd format")

# Validator to prevent the re-use of an email address during registration
def registration_validator(form, field):
    email_in_use = Project.query.filter(User.email == field.data).first()
    if email_in_use:
        raise ValidationError("That email address already has an account")


# Create a login form
class LoginForm(Form):
    email = TextField('Email',
            validators=[Email(message="Must be a valid email address")])
    password = PasswordField('Password',
            validators=[Required(message="You must provide a password")])

# Create a registration form
class RegisterForm(Form):
    email = TextField('Email', validators=[
            Email(message="Must be a valid email address"),
            registration_validator])
    password = PasswordField('Password', validators=[
            Required(message="Must provide a password"),
            EqualTo("confirm_password", message="Passwords must match")])
    confirm_password = PasswordField('Confirm Password')

# Create a new project form
class NewProjectForm(Form):
    existing_project = SelectField("Existing Project")
    new_project = TextField("New Project Name")

# Create a form to select start and end dates for the history view
class HistoryDateForm(Form):
    start_date = DateField("Work On or After This Date (yyyy-mm-dd)",
            default=date(2014, 1, 1),
            validators=[Required("Start date required"), date_validator])
    end_date = DateField("Work On or Before This Date (yyyy-mm-dd)",
            default=datetime.today(),
            validators=[Required("End date required"), date_validator])
