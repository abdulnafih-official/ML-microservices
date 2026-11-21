from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Algo(str, Enum):
    random_forest = "random_forest"
    xgboost = "xgboost"


class TaskType(str, Enum):
    classification = "classification"
    regression = "regression"


class TrainRequestMeta(BaseModel):
    algo: Algo
    task_type: TaskType
    target_col: str
    ai_cleaning: bool = True


class JobOut(BaseModel):
    id: UUID
    status: str
    error: str | None = None
    created_at: datetime
    model_id: UUID | None = None
