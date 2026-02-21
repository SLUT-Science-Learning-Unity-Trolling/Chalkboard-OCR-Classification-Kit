"""DTO для описания ошибок."""

from dataclasses import dataclass


@dataclass(slots=True)
class ProblemDetailsDTO:
  """DTO для описания ошибок."""

  type: str
  title: str
  status: int
  detail: str

