import pandas as pd
import pytest
from fastapi import HTTPException

from app.input_validation import validate_payload


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
