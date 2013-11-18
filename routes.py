from flask import Flask, render_template, redirect, url_for, g, request

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email, Length

from contextlib import closing

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database import session
from models import User, Project


# Set application constants, and create application
DATABASE = '/tmp/timeclock.db'
DEBUG = True
SECRET_KEY = 'whateverrrr'

app = Flask(__name__)
app.config.from_object(__name__)


# Remove the database session at the end of a request or at shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


# Create a login and registration form
class RegisterForm(Form):
    name = TextField('Username', validators=[
            Length(min=1, max=32, message="Maximum username length is 32")])
    email = TextField('Email', validators=[
            Email(message="A valid email address, please")])
    password = PasswordField('Password', validators=[
            Length(min=1, max=32, message="Maximum password length is 32")])
    confirm_password = PasswordField('Confirm Password', validators=[
            Length(min=1, max=32, message="Maximum password length is 32")])

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        # Log the user in here with Flask-Login library
        return redirect('/user_list')
    return render_template('login.html', form=form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data,
                password=form.password.data)
        session.add(user)
        session.commit()
         # Log the user in here with Flask-Login library
        return redirect('/user_list')
    return render_template('register.html', form=form)

@app.route('/current', methods=['POST', 'GET'])
def current():
    pass

@app.route('/today')
def today():
    pass

@app.route('/history', methods=['POST', 'GET'])
def history():
    pass

# For administrative and development purposes, print a list of all users
@app.route('/user_list')
def user_list():
    return render_template('user_list.html', users=User.query.all())

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()
