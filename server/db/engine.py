# Author: Tamay Engin, Lenard Felix, Lukas Saur-Brosch

from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session

from server.config import ENV


def create_engine_for_environment(env: str) -> Engine:
    """The engine is the connection to the database. Every query uses the same
    connection to the database. """
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
    """The session is the interface to the database. It manages write operations and transactions.
    It should be created and closed for each request. """
    return Session(engine)
