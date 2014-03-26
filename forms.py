from datetime import date
import re

from flask.ext.login import current_user
from flask_wtf import Form
from wtforms import DateField, PasswordField, SelectField, TextField
from wtforms.validators import Email, EqualTo, Length, Required,\
        ValidationError

from database import session
from models import User, Project


# Issue: no error text is shown to the user when this validator fails
# Validator to determine whether a date is in WTForms-compatible format
def validate_date_formatting(form, field):
    message = "Dates must be in yyyy-mm-dd format"

    checker = re.compile("(\d{4})\-(\d{2})\-(\d{2})")
    match = date_checker.search()

    if match:
        try:
            month = int(match.groups()[1])
            day = int(match.groups()[2])
            if not 1 <= month <= 12 or not 1 <= day <= 31:
                raise ValidationError(message)
        except:
            raise ValidationError(message)
    else:
        raise ValidationError(message)

# Validator to prevent the re-use of an email address during registration
def validate_user_not_in_use(form, field):
    email_in_use = User.query.filter(User.email == field.data).first()
    if email_in_use:
        raise ValidationError("That email address already has an account")

# Validator to prevent the re-use of an email address during registration
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

    existing_project = SelectField("Existing Project", coerce=int)
    new_project = TextField("New Project Name", validators=[
            validate_exactly_one_field_used,
            validate_project_not_in_use])

# Create a form to select start and end dates for the history view
class HistoryDateForm(Form):
    start_date = DateField("Start Date",
            default=date(2014, 1, 1), validators=[
            Required("Start date required"), validate_date_formatting])
    end_date = DateField("End Date",
            default=date.today(), validators=[
            Required("End date required"), validate_date_formatting])
