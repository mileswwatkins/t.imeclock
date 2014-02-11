from flask import Flask, render_template, redirect, url_for, g, request

from flask.ext.login import LoginManager, login_required, login_user, \
        logout_user, current_user

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Email, Length, EqualTo

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

@app.route('/')
def no_route():
    if current_user.is_authenticated():
        return redirect('/current')
    else:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) == True:
            login_user(user, remember=True)
            return redirect('/user_list')
        else:
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

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

@app.route('/current', methods=['POST', 'GET'])
@login_required
def current():
    pass

@app.route('/history', methods=['POST', 'GET'])
@login_required
def history():
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# For development purposes, print a list of all users
@app.route('/user_list')
def user_list():
    return render_template('user_list.html', users=User.query.all())

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()
