from __future__ import annotations

from enum import StrEnum
from fractions import Fraction
from typing import Annotated, Any, NewType
from uuid import uuid4

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
    model_validator,
)

UserId = NewType("UserId", str)
RecipeId = NewType("RecipeId", str)
FoodId = NewType("FoodId", str)
IngredientId = NewType("IngredientId", str)
StepId = NewType("StepId", str)
OutputId = NewType("OutputId", str)
EquipmentId = NewType("EquipmentId", str)
ComponentId = NewType("ComponentId", str)


def new_id() -> str:
    return uuid4().hex


class Base(BaseModel):
    """``extra="forbid"`` so a typo'd field name fails instead of being dropped."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValueError("amount cannot be a boolean")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(value).limit_denominator(64)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("amount cannot be empty")
        return sum((Fraction(part) for part in text.split()), Fraction(0))
    raise ValueError(f"cannot parse amount from {value!r}")


Exact = Annotated[
    Fraction,
    BeforeValidator(parse_fraction),
    PlainSerializer(str, return_type=str),
    WithJsonSchema({"type": "string", "examples": ["1/2", "3/2", "2"]}),
]


def format_amount(value: Fraction) -> str:
    """``3/2`` → ``"1 1/2"`` for a recipe card."""
    whole, remainder = divmod(abs(value), 1)
    sign = "-" if value < 0 else ""
    if remainder == 0:
        return f"{sign}{whole}"
    if whole == 0:
        return f"{sign}{remainder.numerator}/{remainder.denominator}"
    return f"{sign}{whole} {remainder.numerator}/{remainder.denominator}"


class Amount(Base):
    value: Exact
    upper: Exact | None = None  # "2-3 cloves"
    approximate: bool = False

    @model_validator(mode="after")
    def _check_range(self) -> Amount:
        if self.upper is not None and self.upper <= self.value:
            raise ValueError("upper bound of a range must exceed its lower bound")
        return self

    def scaled(self, factor: Fraction | int) -> Amount:
        factor = Fraction(factor)
        return self.model_copy(
            update={
                "value": self.value * factor,
                "upper": None if self.upper is None else self.upper * factor,
            }
        )

    def __str__(self) -> str:
        if self.upper is None:
            return format_amount(self.value)
        return f"{format_amount(self.value)}-{format_amount(self.upper)}"


class UnitId(StrEnum):
    TSP = "tsp"
    TBSP = "tbsp"
    FLOZ = "fl_oz"
    CUP = "cup"
    PINT = "pint"
    QUART = "quart"
    GALLON = "gallon"
    ML = "ml"
    L = "l"
    GRAM = "g"
    KILOGRAM = "kg"
    OUNCE = "oz"
    POUND = "lb"
    MM = "mm"
    CM = "cm"
    INCH = "inch"
    PIECE = "piece"
    CLOVE = "clove"
    CAN = "can"
    JAR = "jar"
    PACKAGE = "package"
    BUNCH = "bunch"
    HEAD = "head"
    STALK = "stalk"
    SPRIG = "sprig"
    SLICE = "slice"
    STICK = "stick"
    SHEET = "sheet"
    EAR = "ear"
    LEAF = "leaf"
    PINCH = "pinch"
    DASH = "dash"
    DROP = "drop"
    HANDFUL = "handful"


class Quantity(Base):
    """How much of something. Each field is optional, and each absence is meaningful.

    ``2 cans`` (amount + unit), ``1 large onion`` (amount + size),
    ``yogurt and pita`` (nothing).
    """

    amount: Amount | None = None
    unit: UnitId | None = None
    size: str | None = None  # "large", "15 oz each" — not a real unit

    def scaled(self, factor: Fraction | int) -> Quantity:
        if self.amount is None or self.amount.approximate:
            return self
        return self.model_copy(update={"amount": self.amount.scaled(factor)})

    def __str__(self) -> str:
        parts: list[str] = []
        if self.amount is not None:
            parts.append(str(self.amount))
        if self.size:
            parts.append(f"({self.size})" if self.unit else self.size)
        if self.unit is not None:
            parts.append(self.unit.value)
        return " ".join(parts)


class Duration(Base):
    min_minutes: int = Field(ge=0)
    max_minutes: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _check_range(self) -> Duration:
        if self.max_minutes is not None and self.max_minutes <= self.min_minutes:
            raise ValueError("max_minutes must exceed min_minutes")
        return self

    @property
    def longest_minutes(self) -> int:
        return self.max_minutes if self.max_minutes is not None else self.min_minutes

    def __str__(self) -> str:
        if self.max_minutes is None:
            return f"{self.min_minutes} min"
        return f"{self.min_minutes}-{self.max_minutes} min"


class TemperatureUnit(StrEnum):
    F = "F"
    C = "C"


class Temperature(Base):
    value: int
    unit: TemperatureUnit = TemperatureUnit.F

    def __str__(self) -> str:
        return f"{self.value}°{self.unit.value}"


class HeatLevel(StrEnum):
    OFF = "off"
    LOW = "low"
    MEDIUM_LOW = "medium-low"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium-high"
    HIGH = "high"
