from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .common import (
    Base,
    ComponentId,
    Duration,
    EquipmentId,
    Exact,
    HeatLevel,
    IngredientId,
    OutputId,
    Quantity,
    StepId,
    new_id,
)
from .technique import Technique


class Equipment(Base):
    id: EquipmentId = Field(default_factory=lambda: EquipmentId(new_id()))
    name: str  # "Dutch oven", "sheet pan", "stand mixer"
    size: str | None = None  # "large", "9x13", "12-inch"


class Portion(Base):
    fraction: Exact | None = None
    quantity: Quantity | None = None
    note: str | None = None  # "plus more for drizzling"

    @model_validator(mode="after")
    def _one_measure(self) -> Portion:
        if self.fraction is not None and self.quantity is not None:
            raise ValueError("set fraction or quantity, not both")
        if self.fraction is not None and not (0 < self.fraction <= 1):
            raise ValueError("portion fraction must be within (0, 1]")
        return self


class IngredientRef(Base):
    ref: Literal["ingredient"] = "ingredient"
    ingredient_id: IngredientId
    portion: Portion | None = None  # None means all of it


class StepRef(Base):
    """This step consumes what an earlier step produced."""
    ref: Literal["step"] = "step"
    step_id: StepId
    output_id: OutputId | None = None
    portion: Portion | None = None


StepInput = Annotated[IngredientRef | StepRef, Field(discriminator="ref")]


class Reserved(Base):
    """A secondary output set aside for later: "fry, then crush -- reserve 1 cup"."""

    id: OutputId = Field(default_factory=lambda: OutputId(new_id()))
    name: str  # "reserved chickpeas", "pasta water"
    quantity: Quantity | None = None


class Step(Base):
    """
    A step's *primary* output is implicit and is referenced by the step's own
    id; ``reserves`` covers the rarer case of setting something aside. The
    fully general alternative -- a list of outputs on every step -- makes the
    overwhelmingly common single-output step noisier to write and to consume.
    """

    id: StepId = Field(default_factory=lambda: StepId(new_id()))
    technique: Technique
    inputs: list[StepInput] = Field(default_factory=list)

    label: str 
    text: str | None = None

    duration: Duration | None = None
    until: str | None = None 
    heat: HeatLevel | None = None
    attention: str | None = None 
    vessel: EquipmentId | None = None

    reserves: list[Reserved] = Field(default_factory=list)
    component: ComponentId | None = None
    order: int | None = None

    @property
    def is_banner(self) -> bool:
        """Input-less steps (setup, preheat) render full-width in the grid."""
        return not self.inputs

    @property
    def ingredient_inputs(self) -> list[IngredientRef]:
        return [i for i in self.inputs if isinstance(i, IngredientRef)]

    @property
    def step_inputs(self) -> list[StepRef]:
        return [i for i in self.inputs if isinstance(i, StepRef)]

    @property
    def outputs(self) -> list[OutputId]:
        """Every id a later step may point at: the primary output plus reserves."""
        return [OutputId(self.id), *(r.id for r in self.reserves)]

    def __str__(self) -> str:
        if self.text:
            return self.text
        parts = [self.label]
        if self.duration is not None:
            parts.append(str(self.duration))
        if self.until:
            parts.append(self.until)
        if self.attention:
            parts.append(self.attention)
        return " · ".join(parts)
