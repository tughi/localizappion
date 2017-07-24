from schema import Language, Project, String, Suggestion, Translator, Vote


def create_scoped_session(database_url):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine(database_url, echo=True)
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_database(session):
    from schema import Base

    Base.metadata.create_all(session.bind)
