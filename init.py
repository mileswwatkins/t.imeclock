from database import Base, engine
from models import User, Project, Spell


def init_db():
    """Run to initiate database for the program."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
	init_db()
