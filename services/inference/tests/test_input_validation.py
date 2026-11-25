import pandas as pd
import pytest
from fastapi import HTTPException

from app.input_validation import validate_batch_payload, validate_payload


def test_missing_field_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_payload({"age": 20}, {"age": "number", "name": "string"})
    assert exc.value.status_code == 422


def test_extra_field_rejected():
    with pytest.raises(HTTPException):
        validate_payload({"age": 20, "name": "A", "extra": 1}, {"age": "number", "name": "string"})


def test_wrong_type_rejected():
    with pytest.raises(HTTPException):
        validate_payload({"age": "old", "name": "A"}, {"age": "number", "name": "string"})


def test_valid_payload_returns_dataframe():
    frame = validate_payload({"age": 20, "name": "A"}, {"age": "number", "name": "string"})
    assert isinstance(frame, pd.DataFrame)
    assert list(frame.columns) == ["age", "name"]


def test_valid_batch_payload_returns_all_rows_in_schema_order():
    frame = validate_batch_payload(
        [{"name": "A", "age": 20}, {"name": "B", "age": 30}],
        {"age": "number", "name": "string"},
        max_rows=2,
    )
    assert list(frame.columns) == ["age", "name"]
    assert frame.to_dict(orient="records") == [
        {"age": 20.0, "name": "A"},
        {"age": 30.0, "name": "B"},
    ]


@pytest.mark.parametrize(
    ("payload", "max_rows", "expected_status"),
    [
        ([], 2, 422),
        ([{"age": 20, "name": "A"}, {"age": 30, "name": "B"}], 1, 413),
        ([{"age": "old", "name": "A"}], 2, 422),
    ],
)
def test_invalid_batch_payload_is_rejected(payload, max_rows, expected_status):
    with pytest.raises(HTTPException) as exc:
        validate_batch_payload(payload, {"age": "number", "name": "string"}, max_rows)
    assert exc.value.status_code == expected_status
