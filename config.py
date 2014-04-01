from flask import Flask, g
from flask.ext.login import LoginManager, current_user

from database import session
from models import User


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
