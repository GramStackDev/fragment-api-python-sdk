from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from fragment._compat import StrEnum


class ServiceType(StrEnum):
    PREMIUM = "premium"
    STARS = "stars"


class FragmentUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    recipient: str
    photo: str
