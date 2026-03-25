# Author: Tamay Engin

from sqlmodel import Field, SQLModel, create_engine

def engine(mode: str, disk: bool):
    url = ""
    if mode != "prod" | !disk
        url = "sqlite:///:memory:"
    else:
        url = "sqlite:///database.db"
    engine = create_engine(url, echo=True)
    SQLModel.metadata.create_all(engine)
    return engine
