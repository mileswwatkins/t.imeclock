from datetime import datetime
import re

from flask import request
from flask.ext.login import current_user
from flask_wtf import Form
from sqlalchemy import func
from wtforms import PasswordField, SelectField, TextField
from wtforms.validators import Email, EqualTo, Length, Regexp, Required,\
        ValidationError
from wtforms.ext.dateutil.fields import DateField

from config import app
from database import session
from models import User, Project, Spell
from utility import guess_user_timezone


# Validator to prevent the re-use of an email address during registration
def validate_user_not_in_use(form, field):
    email_in_use = User.query.filter(User.email == field.data).first()
    if email_in_use:
        raise ValidationError("That email address already has an account")

# Validator to prevent the re-use of a project name during registration
def validate_project_not_in_use(form, field):
    project_in_use = Project.query.\
            filter(Project.name == field.data).\
            filter(Project.user_id == current_user.id).\
            first()
    if project_in_use:
        raise ValidationError("That project name is already in use")


# Create a login form
class LoginForm(Form):
    email = TextField("Email",
            validators=[Email(message="Must be a valid email address")])
    password = PasswordField("Password",
            validators=[Required(message="You must provide a password")])

# Create a registration form
class RegisterForm(Form):
    email = TextField("Email", validators=[
            Email(message="Must be a valid email address"),
            validate_user_not_in_use])
    password = PasswordField("Password", validators=[
            Required(message="Must provide a password"),
            EqualTo("confirm_password", message="Passwords must match")])
    confirm_password = PasswordField("Confirm Password")

# Create a switch project form
class SwitchProjectForm(Form):
    # Validator to ensure that exactly one of the SelectField and
    # TextField was used when switching projects in the current view
    def validate_exactly_one_field_used(self, field):
        message = "Must either select an existing project OR create a new one"
        if self.existing_project.data and self.new_project.data:
            raise ValidationError(message)
        elif not self.existing_project.data and not self.new_project.data:
            raise ValidationError(message)

    pattern_forbidding_extra_spaces = "^(\S+(\s\S+)*)*$"

    existing_project = SelectField("Existing Project", coerce=int)
    new_project = TextField("New Project Name", validators=[
            validate_exactly_one_field_used,
            validate_project_not_in_use,
            Regexp(regex=pattern_forbidding_extra_spaces,
            message="No extra spaces are allowed in project names")])

# Create a form to select start and end dates for the history view
class HistoryDateForm(Form):
    # Due to request context issues, cannot access the user's timezone
    default_date = datetime.now(None).today()
    start_date = DateField("Start Date", default=default_date)
    end_date = DateField("End Date", default=default_date)
