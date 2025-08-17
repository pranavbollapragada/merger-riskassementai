from pydantic import BaseModel
from typing import List

class QuarterlyRiskInput(BaseModel):
    quarters: List[str]  # e.g., ["2023-Q1", "2023-Q2", "2023-Q3"]
    penalty_per_year: List[float]
    percent_returns_late: List[float]
