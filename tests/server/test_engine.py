# Author: Lenard Felix

# mypy: disable-error-code=import-not-found

from __future__ import annotations

from sqlalchemy import text
from sqlmodel import Session

from server.db.engine import create_engine_for_environment


def test_create_engine_for_test_environment_opens_session() -> None:
    engine = create_engine_for_environment("test")

    with Session(engine) as session:
        result = session.execute(text("SELECT 1")).scalar_one()

    assert result == 1
