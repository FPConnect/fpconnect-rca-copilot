from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def make_engine(database_url: str):
    return create_engine(database_url, pool_pre_ping=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
