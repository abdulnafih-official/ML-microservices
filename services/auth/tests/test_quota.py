from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy.dialects import postgresql

from app.quota import get_usage, reserve_slot


class FakeDB:
    def __init__(self, models_trained=0, models_reserved=0, rowcount=1):
        self.user = SimpleNamespace(
            models_trained=models_trained,
            models_reserved=models_reserved,
        )
        self.rowcount = rowcount
        self.statement = None

    def get(self, model, user_id):
        return self.user

    def execute(self, statement):
        self.statement = statement
        return SimpleNamespace(rowcount=self.rowcount)

    def commit(self):
        pass


def test_usage_includes_trained_and_reserved_models():
    assert get_usage(FakeDB(models_trained=1, models_reserved=1), uuid4(), 2) == (2, 2)


def test_reservation_limit_includes_already_trained_models():
    db = FakeDB(rowcount=0)

    assert reserve_slot(db, uuid4(), 2) is False
    compiled = str(db.statement.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True},
    ))
    assert "models_trained + auth.users.models_reserved < 2" in compiled