# Author: Tamay Engin, Lenard Felix

from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session

from server.config import ENV


def create_engine_for_environment(env: str) -> Engine:
    echo = (env == "dev")

    if env == "test":
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )

    db_url = f"sqlite:///./data/{env}.db"

    return create_engine(db_url, echo=echo)


engine = create_engine_for_environment(ENV)


def get_session():
    return Session(engine)
