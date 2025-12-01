from sqlmodel import Session, create_engine

from app.core.config import Config

engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)


def get_session() -> Session:
    return Session(engine)
