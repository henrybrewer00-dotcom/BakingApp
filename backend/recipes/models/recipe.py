from __future__ import annotations

from collections import Counter
from datetime import datetime
from enum import StrEnum
from fractions import Fraction

from pydantic import Field, HttpUrl, model_validator

from .common import (
    Amount,
    Base,
    ComponentId,
    IngredientId,
    RecipeId,
    StepId,
    UserId,
    new_id,
)
from .food import RecipeIngredient
from .step import Equipment, IngredientRef, Step, StepRef
from .user import Attribution


class ComponentKind(StrEnum):
    """What sort of sub-assembly this is.

    An enum plus a free ``name``, rather than a ``Dough`` subclass: reach for a
    discriminated union when the *fields* differ (as with ``Technique``, where
    ``Bake`` needs a temperature ``Dice`` has no use for), and an enum when only
    the *label* differs. Dough, glaze and filling have the identical shape -- a
    name, some ingredients, some steps, one output -- so subclassing buys no
    fields and costs a union match at every render site.
    """

    DOUGH = "dough"
    BATTER = "batter"
    FILLING = "filling"
    FROSTING = "frosting"
    GLAZE = "glaze"
    SAUCE = "sauce"
    TOPPING = "topping"
    CRUST = "crust"
    STREUSEL = "streusel"
    MARINADE = "marinade"
    ASSEMBLY = "assembly"
    OTHER = "other"


class Component(Base):
    """A named sub-assembly: the dough, the glaze, the spice paste.

    Really a sub-DAG. Its terminal step's output is what some later step
    consumes, which is also the seam the grid renderer draws the merge at.
    Ingredients and steps point *at* a component by id rather than nesting
    inside it, so an assembly step can consume the dough and the filling
    without awkward cross-nesting.
    """

    id: ComponentId = Field(default_factory=lambda: ComponentId(new_id()))
    name: str  # "Brioche dough", "Lemon glaze"
    kind: ComponentKind = ComponentKind.OTHER
    order: int | None = None


class Yield(Base):
    amount: Amount
    unit: str  # "servings", "cookies", "loaf"

    def scaled(self, factor: Fraction | int) -> Yield:
        return self.model_copy(update={"amount": self.amount.scaled(factor)})

    def __str__(self) -> str:
        return f"{self.amount} {self.unit}"


class Course(StrEnum):
    BREAKFAST = "breakfast"
    APPETIZER = "appetizer"
    MAIN = "main"
    SIDE = "side"
    SOUP = "soup"
    SALAD = "salad"
    BREAD = "bread"
    DESSERT = "dessert"
    DRINK = "drink"
    SAUCE = "sauce"
    SNACK = "snack"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Visibility(StrEnum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class Image(Base):
    url: HttpUrl
    alt: str | None = None
    caption: str | None = None
    is_primary: bool = False


class Note(Base):
    """A tip or amendment, distinct from the headnote: written after the fact."""

    id: str = Field(default_factory=new_id)
    author: UserId | None = None
    text: str
    created_at: datetime = Field(default_factory=datetime.now)


class Recipe(Base):
    id: RecipeId = Field(default_factory=lambda: RecipeId(new_id()))
    slug: str
    title: str
    headnote: str | None = None  # the story paragraph above the recipe

    #: Whose recipe it is -- often not a site user (a cookbook, a grandmother).
    owner: Attribution
    #: Who typed it into this site. Always an account here.
    added_by: UserId

    yields: Yield | None = None
    ingredients: list[RecipeIngredient] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
    equipment: list[Equipment] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
    cuisine: str | None = None
    course: Course | None = None
    difficulty: Difficulty | None = None

    images: list[Image] = Field(default_factory=list)
    notes: list[Note] = Field(default_factory=list)
    source_url: HttpUrl | None = None

    forked_from: RecipeId | None = None
    visibility: Visibility = Visibility.PRIVATE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def _fill_ordering(self) -> Recipe:
        for index, ingredient in enumerate(self.ingredients):
            if ingredient.display_order is None:
                ingredient.display_order = index
        for index, step in enumerate(self.steps):
            if step.order is None:
                step.order = index
        for index, component in enumerate(self.components):
            if component.order is None:
                component.order = index
        return self

    @model_validator(mode="after")
    def _unique_ids(self) -> Recipe:
        for label, ids in (
            ("ingredient", [i.id for i in self.ingredients]),
            ("step", [s.id for s in self.steps]),
            ("component", [c.id for c in self.components]),
            ("equipment", [e.id for e in self.equipment]),
            ("output", [o for s in self.steps for o in s.outputs]),
        ):
            duplicates = [key for key, count in Counter(ids).items() if count > 1]
            if duplicates:
                raise ValueError(f"duplicate {label} id(s): {sorted(duplicates)}")
        return self

    @model_validator(mode="after")
    def _references_resolve(self) -> Recipe:
        ingredient_ids = {i.id for i in self.ingredients}
        component_ids = {c.id for c in self.components}
        equipment_ids = {e.id for e in self.equipment}
        outputs_by_step = {s.id: set(s.outputs) for s in self.steps}

        for ingredient in self.ingredients:
            if ingredient.component is not None and ingredient.component not in component_ids:
                raise ValueError(f"ingredient {ingredient.id} names unknown component")

        for step in self.steps:
            if step.component is not None and step.component not in component_ids:
                raise ValueError(f"step {step.id} names unknown component")
            if step.vessel is not None and step.vessel not in equipment_ids:
                raise ValueError(f"step {step.id} names unknown equipment {step.vessel}")

            # Techniques may embed an ingredient reference of their own.
            fat = getattr(step.technique, "fat", None)
            if fat is not None and fat not in ingredient_ids:
                raise ValueError(f"step {step.id} names unknown fat ingredient {fat}")

            for ref in step.inputs:
                if isinstance(ref, IngredientRef):
                    if ref.ingredient_id not in ingredient_ids:
                        raise ValueError(
                            f"step {step.id} consumes unknown ingredient {ref.ingredient_id}"
                        )
                else:
                    if ref.step_id not in outputs_by_step:
                        raise ValueError(f"step {step.id} consumes unknown step {ref.step_id}")
                    if (
                        ref.output_id is not None
                        and ref.output_id not in outputs_by_step[ref.step_id]
                    ):
                        raise ValueError(
                            f"step {step.id} consumes output {ref.output_id}, "
                            f"which step {ref.step_id} does not produce"
                        )
        return self

    @model_validator(mode="after")
    def _readable_top_to_bottom(self) -> Recipe:
        """Every step must come after the steps it consumes.

        Distinct orders plus strictly backward references is the same thing as
        acyclicity, so this one check covers both invariants.
        """
        order_of: dict[StepId, int] = {}
        for step in self.steps:
            assert step.order is not None  # filled by _fill_ordering
            order_of[step.id] = step.order

        if len(set(order_of.values())) != len(order_of):
            raise ValueError("step orders must be distinct")

        for step in self.steps:
            for ref in step.step_inputs:
                if order_of[ref.step_id] >= order_of[step.id]:
                    raise ValueError(
                        f"step {step.id} consumes step {ref.step_id}, which does not "
                        "come before it"
                    )
        return self

    # ------------------------------------------------------------------ #
    # Derived views
    # ------------------------------------------------------------------ #

    @property
    def steps_in_order(self) -> list[Step]:
        return sorted(self.steps, key=lambda s: s.order or 0)

    @property
    def ingredients_in_order(self) -> list[RecipeIngredient]:
        return sorted(self.ingredients, key=lambda i: i.display_order or 0)

    @property
    def components_in_order(self) -> list[Component]:
        return sorted(self.components, key=lambda c: c.order or 0)

    @property
    def total_time_minutes(self) -> int:
        return sum(s.duration.longest_minutes for s in self.steps if s.duration)

    def grid_row_order(self) -> list[IngredientId]:
        """Ingredient ordering that makes each step's inputs a contiguous block.

        Walks the steps in order and emits each ingredient the first time it is
        consumed, then appends anything never consumed. Contiguity holds within
        a single chain; a recipe that builds two components in parallel yields
        one staircase per component, merging at the assembly step.
        """
        order: list[IngredientId] = []
        seen: set[IngredientId] = set()
        for step in self.steps_in_order:
            for ref in step.ingredient_inputs:
                if ref.ingredient_id not in seen:
                    seen.add(ref.ingredient_id)
                    order.append(ref.ingredient_id)
        for ingredient in self.ingredients_in_order:
            if ingredient.id not in seen:
                order.append(ingredient.id)
        return order

    # ------------------------------------------------------------------ #
    # Soft checks -- warnings for the editor, not validation errors
    # ------------------------------------------------------------------ #

    def unused_ingredients(self) -> list[RecipeIngredient]:
        """Ingredients no step consumes."""
        used = {
            ref.ingredient_id for step in self.steps for ref in step.ingredient_inputs
        }
        used |= {
            fat
            for step in self.steps
            if (fat := getattr(step.technique, "fat", None)) is not None
        }
        return [i for i in self.ingredients_in_order if i.id not in used]

    def terminal_steps(self) -> list[Step]:
        """Steps nothing else consumes. A finished recipe has exactly one."""
        consumed = {ref.step_id for step in self.steps for ref in step.step_inputs}
        return [s for s in self.steps_in_order if s.id not in consumed and s.inputs]

    # ------------------------------------------------------------------ #
    # Operations
    # ------------------------------------------------------------------ #

    def scaled(self, factor: Fraction | int) -> Recipe:
        """Halve or double a recipe. Exact rationals, so thirds stay thirds."""
        clone = self.model_copy(deep=True)
        for ingredient in clone.ingredients:
            ingredient.quantity = ingredient.quantity.scaled(factor)
        if clone.yields is not None:
            clone.yields = clone.yields.scaled(factor)
        return clone
