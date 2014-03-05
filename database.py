import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configure SQLAlchemy database
if os.environ.get('DATABASE_URL') is None:
	SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/timeclock.db'
else:
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
engine = create_engine(SQLALCHEMY_DATABASE_URI)
session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
        ))
Base = declarative_base()
Base.query = session.query_property()

# Function to initialize the database
def init_db():
    '''Run interactively to initiate database for the program.'''
    from models import User, Project
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
	init_db()
