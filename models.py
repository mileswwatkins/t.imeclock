from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    projects = relationship('Project')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User {}>'.format(self.name)


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
