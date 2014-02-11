from datetime import datetime

from md5 import md5

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    projects = relationship('Project')

    def __init__(self, email, password):
        self.email = email
        self.password = md5(password).hexdigest()

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def check_password(self, entered_password):
        if md5(entered_password).hexdigest() == self.password:
            return True
        else:
            return False


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    start = Column(DateTime)
    end = Column(DateTime)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Project {0} for user {1}>'.format(self.name, self.user_id)
