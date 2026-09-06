from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import EmailStr, Field, HttpUrl

from .common import Base, UserId, new_id


class User(Base):
    id: UserId = Field(default_factory=lambda: UserId(new_id()))
    display_name: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.now)


class UserAttribution(Base):
    """The recipe belongs to someone with an account here."""

    kind: Literal["user"] = "user"
    user_id: UserId


class ExternalAttribution(Base):
    """The recipe belongs to Grandma, a cookbook, or a site."""

    kind: Literal["external"] = "external"
    name: str  # "Alison Roman", "Grandma Ruth"
    source: str | None = None  # book or publication title
    url: HttpUrl | None = None
    page: str | None = None


Attribution = Annotated[
    UserAttribution | ExternalAttribution,
    Field(discriminator="kind"),
]
