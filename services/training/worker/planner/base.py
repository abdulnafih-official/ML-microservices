from abc import ABC, abstractmethod


class Planner(ABC):
    @abstractmethod
    def plan(self, profile: dict, task_type: str, target_col: str) -> dict:
        """Return a raw cleaning plan."""
