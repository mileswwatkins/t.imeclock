from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import backref, relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    projects = relationship("Project", order_by="Project.name", backref="user")

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return "<User {}>".format(self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def check_password(self, entered_password):
        return check_password_hash(self.password, entered_password)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)

    spells = relationship("Spell", order_by="Spell.start", backref="project")

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return "<Project {0} for user {1}>".format(self.name, self.user_id)


class Spell(Base):
    __tablename__ = "spells"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    start = Column(DateTime, nullable=False)
    duration = Column(Interval)
    
    def __init__(self, project_id):
        self.project_id = project_id
        self.start = datetime.now()

    def __repr__(self):
        return "<Spell starting at {0} for project {1}>".\
                format(self.name, self.project_id)
