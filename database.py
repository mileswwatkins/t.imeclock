from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Configure SQLAlchemy database
engine = create_engine('sqlite:////tmp/timeclock.db')
session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
        ))
Base = declarative_base()
Base.query = session.query_property()

def init_db():
    '''Run interactively to initiate database for the program.'''
    from models import User, Project
    Base.metadata.create_all(bind=engine)
