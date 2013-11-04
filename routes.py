from flask import Flask, render_template, redirect, url_for, g, request
from contextlib import closing

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database import session
from models import User, Project


# Set application constants, and create application
DATABASE = '/tmp/timeclock.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


# Remove the database session at the end of a request or at shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


# Add a new user based on the URL, and print their name out
@app.route('/new_user/<username>')
def new_user(username):
    user = User(username)
    session.add(user)
    session.commit()
    return "User added: {}".format(username)

# Print list of all users
@app.route('/user_list')
def user_list():
    if User.query.all() is not []:
        all_users = ''
        for user in User.query.all():
            all_users = all_users + user.name + ' '
        return all_users
    else:
        return "No users in database"

@app.route('/new_user_form', methods=['POST', 'GET'])
def new_user_form():
    if request.method == 'POST':
        user = User(request.form['username'])
        session.add(user)
        session.commit()
    return render_template('new_user_form.html')


if __name__ == '__main__':
    app.run()
