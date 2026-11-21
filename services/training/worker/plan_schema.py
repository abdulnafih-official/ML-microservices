from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Action(str, Enum):
    keep = "keep"
    drop = "drop"


class Impute(str, Enum):
    median = "median"
    mean = "mean"
    mode = "mode"
    constant = "constant"
    none = "none"


class Encode(str, Enum):
    onehot = "onehot"
    ordinal = "ordinal"
    none = "none"


class Scale(str, Enum):
    none = "none"
    standard = "standard"


class ColumnPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    action: Action
    reason: str
    impute: Impute = Impute.none
    encode: Encode = Encode.none
    scale: Scale = Scale.none


class CleaningPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    columns: list[ColumnPlan]
    row_rules: dict = Field(default_factory=lambda: {"drop_missing_target": True})
