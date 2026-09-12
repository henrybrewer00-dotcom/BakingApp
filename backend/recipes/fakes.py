"""Stable MVP fixtures: one user, a catalog of foods, and recipes they own.

``FakeRecipe`` is the page mock — gridable, two components, bake temp, notes.
``FakeRecipes`` is the user-page list (the mock plus a simple cookie and a
not-gridable toast so empty states have something to render).

IDs are readable and fixed so the frontend can hardcode routes.
"""

from __future__ import annotations

from datetime import datetime

from recipes.models import (
    Allergen,
    Amount,
    Bake,
    Component,
    ComponentId,
    ComponentKind,
    Course,
    Difficulty,
    Divide,
    Duration,
    Equipment,
    EquipmentId,
    ExternalAttribution,
    FoodCategory,
    FoodId,
    FoodItem,
    Image,
    IngredientId,
    IngredientRef,
    Knead,
    Note,
    Plain,
    Preheat,
    Proof,
    Quantity,
    Recipe,
    RecipeId,
    RecipeIngredient,
    Roll,
    Shape,
    Step,
    StepId,
    StepRef,
    Temperature,
    UnitId,
    User,
    UserAttribution,
    UserId,
    Visibility,
    Yield,
)

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _qty(
    value: str | int | None = None,
    unit: UnitId | None = None,
    size: str | None = None,
    *,
    upper: str | int | None = None,
    approx: bool = False,
) -> Quantity:
    if value is None and not approx:
        return Quantity(unit=unit, size=size)
    return Quantity(
        amount=Amount(value=value if value is not None else 0, upper=upper, approximate=approx),
        unit=unit,
        size=size,
    )


def _food(
    id: str,
    name: str,
    plural: str,
    category: FoodCategory,
    *,
    unit: UnitId | None = None,
    allergens: list[Allergen] | None = None,
) -> FoodItem:
    return FoodItem(
        id=FoodId(id),
        name=name,
        plural_name=plural,
        category=category,
        default_unit=unit,
        allergens=allergens or [],
    )


def _ing(
    id: str,
    food: FoodItem,
    quantity: Quantity,
    *,
    component: str | None = None,
    prep: str | None = None,
    note: str | None = None,
) -> RecipeIngredient:
    return RecipeIngredient(
        id=IngredientId(id),
        food=food.id,
        quantity=quantity,
        component=None if component is None else ComponentId(component),
        prep=prep,
        note=note,
    )


def _iref(ingredient: RecipeIngredient) -> IngredientRef:
    return IngredientRef(ingredient_id=ingredient.id)


def _sref(step: Step) -> StepRef:
    return StepRef(step_id=step.id)


# --------------------------------------------------------------------------- #
# User
# --------------------------------------------------------------------------- #

FakeUser = User(
    id=UserId("ruth"),
    display_name="Ruth Brewer",
    email="ruth@example.com",
    created_at=datetime(2019, 6, 1, 9, 0, 0),
)

# --------------------------------------------------------------------------- #
# Foods — shared across FakeRecipes so the frontend can join names
# --------------------------------------------------------------------------- #

FLOUR = _food("flour", "all-purpose flour", "all-purpose flour", FoodCategory.FLOUR, unit=UnitId.CUP, allergens=[Allergen.WHEAT, Allergen.GLUTEN])
SUGAR = _food("sugar", "sugar", "sugar", FoodCategory.SUGAR, unit=UnitId.CUP)
BROWN_SUGAR = _food("brown-sugar", "brown sugar", "brown sugar", FoodCategory.SUGAR, unit=UnitId.CUP)
POWDERED_SUGAR = _food("powdered-sugar", "powdered sugar", "powdered sugar", FoodCategory.SUGAR, unit=UnitId.CUP)
SALT = _food("salt", "kosher salt", "kosher salt", FoodCategory.SPICE, unit=UnitId.TSP)
YEAST = _food("yeast", "active dry yeast", "active dry yeast", FoodCategory.LEAVENER, unit=UnitId.TSP)
MILK = _food("milk", "whole milk", "whole milk", FoodCategory.DAIRY, unit=UnitId.CUP, allergens=[Allergen.MILK])
BUTTER = _food("butter", "unsalted butter", "unsalted butter", FoodCategory.FAT, unit=UnitId.CUP, allergens=[Allergen.MILK])
EGG = _food("egg", "egg", "eggs", FoodCategory.EGG, allergens=[Allergen.EGG])
CINNAMON = _food("cinnamon", "cinnamon", "cinnamon", FoodCategory.SPICE, unit=UnitId.TBSP)
CREAM_CHEESE = _food("cream-cheese", "cream cheese", "cream cheese", FoodCategory.DAIRY, unit=UnitId.OUNCE, allergens=[Allergen.MILK])
VANILLA = _food("vanilla", "vanilla extract", "vanilla extract", FoodCategory.CONDIMENT, unit=UnitId.TSP)
BAKING_SODA = _food("baking-soda", "baking soda", "baking soda", FoodCategory.LEAVENER, unit=UnitId.TSP)
CHOCOLATE = _food("chocolate-chips", "semisweet chocolate chips", "semisweet chocolate chips", FoodCategory.SUGAR, unit=UnitId.CUP)
BREAD = _food("bread", "sandwich bread", "sandwich bread", FoodCategory.GRAIN, unit=UnitId.SLICE, allergens=[Allergen.WHEAT, Allergen.GLUTEN])

FakeFoods: list[FoodItem] = [
    FLOUR, SUGAR, BROWN_SUGAR, POWDERED_SUGAR, SALT, YEAST, MILK, BUTTER, EGG,
    CINNAMON, CREAM_CHEESE, VANILLA, BAKING_SODA, CHOCOLATE, BREAD,
]

# --------------------------------------------------------------------------- #
# FakeRecipe — Ruth's cinnamon rolls (the recipe-page mock)
# --------------------------------------------------------------------------- #

_DOUGH = Component(id=ComponentId("dough"), name="the dough", kind=ComponentKind.DOUGH)
_FILLING = Component(id=ComponentId("filling"), name="the filling", kind=ComponentKind.FILLING)
_ICING = Component(id=ComponentId("icing"), name="the icing", kind=ComponentKind.FROSTING)

_MIXER = Equipment(id=EquipmentId("mixer"), name="stand mixer", size="bowl fitted with the dough hook")
_PAN = Equipment(id=EquipmentId("pan"), name="baking pan", size="9x13")

_milk = _ing("dough-milk", MILK, _qty("3/4", UnitId.CUP), component="dough", prep="warm")
_yeast = _ing("dough-yeast", YEAST, _qty("2 1/4", UnitId.TSP), component="dough")
_d_sugar = _ing("dough-sugar", SUGAR, _qty("1/4", UnitId.CUP), component="dough")
_d_egg = _ing("dough-egg", EGG, _qty(1), component="dough")
_d_butter = _ing("dough-butter", BUTTER, _qty("1/4", UnitId.CUP), component="dough", prep="melted")
_d_flour = _ing("dough-flour", FLOUR, _qty(3, UnitId.CUP), component="dough")
_d_salt = _ing("dough-salt", SALT, _qty(1, UnitId.TSP), component="dough")

_f_butter = _ing("fill-butter", BUTTER, _qty("1/2", UnitId.CUP), component="filling", prep="softened")
_f_brown = _ing("fill-brown", BROWN_SUGAR, _qty("3/4", UnitId.CUP), component="filling", prep="packed")
_f_cinnamon = _ing("fill-cinnamon", CINNAMON, _qty(2, UnitId.TBSP), component="filling")

_i_cheese = _ing("icing-cheese", CREAM_CHEESE, _qty(4, UnitId.OUNCE), component="icing", prep="softened")
_i_butter = _ing("icing-butter", BUTTER, _qty("1/4", UnitId.CUP), component="icing", prep="softened")
_i_powdered = _ing("icing-powdered", POWDERED_SUGAR, _qty(1, UnitId.CUP), component="icing")
_i_vanilla = _ing("icing-vanilla", VANILLA, _qty("1/2", UnitId.TSP), component="icing")

_bloom = Step(
    id=StepId("bloom"),
    technique=Plain(kind="mix"),
    label="bloom the yeast",
    text="Stir the 3/4 cup warm milk, 2 1/4 tsp yeast, and 1/4 cup sugar. Wait until it foams.",
    inputs=[_iref(_milk), _iref(_yeast), _iref(_d_sugar)],
    duration=Duration(min_minutes=5, max_minutes=10),
    until="until foamy",
    component=ComponentId("dough"),
    vessel=_MIXER.id,
)
_wet = Step(
    id=StepId("wet"),
    technique=Plain(kind="mix"),
    label="mix the wet dough",
    text="Beat in the egg and the 1/4 cup melted butter.",
    inputs=[_sref(_bloom), _iref(_d_egg), _iref(_d_butter)],
    component=ComponentId("dough"),
    vessel=_MIXER.id,
)
_knead = Step(
    id=StepId("knead"),
    technique=Knead(method="stand_mixer"),
    label="knead",
    text="Add the 3 cups flour and 1 tsp salt. Knead on medium until the dough is smooth and pulls from the bowl.",
    inputs=[_sref(_wet), _iref(_d_flour), _iref(_d_salt)],
    duration=Duration(min_minutes=8),
    until="until smooth",
    component=ComponentId("dough"),
    vessel=_MIXER.id,
)
_proof1 = Step(
    id=StepId("proof-1"),
    technique=Proof(covered=True),
    label="first rise",
    text="Cover and let rise until doubled.",
    inputs=[_sref(_knead)],
    duration=Duration(min_minutes=60, max_minutes=90),
    until="until doubled",
    component=ComponentId("dough"),
)
_mix_filling = Step(
    id=StepId("mix-filling"),
    technique=Plain(kind="combine"),
    label="make the filling",
    text="Mash the 1/2 cup softened butter with 3/4 cup brown sugar and 2 tbsp cinnamon into a paste.",
    inputs=[_iref(_f_butter), _iref(_f_brown), _iref(_f_cinnamon)],
    component=ComponentId("filling"),
)
_roll = Step(
    id=StepId("roll"),
    technique=Roll(thickness="1/4 inch"),
    label="roll the dough",
    text="Punch down and roll into a 12-by-16-inch rectangle, about 1/4 inch thick.",
    inputs=[_sref(_proof1)],
    component=ComponentId("dough"),
)
_fill = Step(
    id=StepId("fill"),
    technique=Plain(kind="assemble"),
    label="spread the filling",
    text="Spread the cinnamon butter over the dough, leaving a 1/2-inch strip along one long edge.",
    inputs=[_sref(_roll), _sref(_mix_filling)],
    component=ComponentId("filling"),
)
_shape = Step(
    id=StepId("shape"),
    technique=Shape(form="log"),
    label="roll into a log",
    text="Roll up from the long side into a tight log and pinch the seam.",
    inputs=[_sref(_fill)],
)
_divide = Step(
    id=StepId("divide"),
    technique=Divide(portions=12),
    label="cut into 12",
    text="Slice the log into 12 rolls and nestle them in a buttered 9x13 pan.",
    inputs=[_sref(_shape)],
    vessel=_PAN.id,
)
_proof2 = Step(
    id=StepId("proof-2"),
    technique=Proof(covered=True),
    label="second rise",
    text="Cover and let the rolls puff until they touch.",
    inputs=[_sref(_divide)],
    duration=Duration(min_minutes=30, max_minutes=45),
    until="until puffy and touching",
    vessel=_PAN.id,
)
_preheat = Step(
    id=StepId("preheat"),
    technique=Preheat(temperature=Temperature(value=350)),
    label="heat the oven to 350°F",
)
_bake = Step(
    id=StepId("bake"),
    technique=Bake(temperature=Temperature(value=350), rack="middle"),
    label="bake",
    text="Bake until the tops are golden and the centers are set.",
    inputs=[_sref(_proof2)],
    duration=Duration(min_minutes=25, max_minutes=30),
    until="until golden",
    vessel=_PAN.id,
)
_mix_icing = Step(
    id=StepId("mix-icing"),
    technique=Plain(kind="cream"),
    label="beat the icing",
    text="Beat the cream cheese and butter until smooth, then the powdered sugar and vanilla.",
    inputs=[_iref(_i_cheese), _iref(_i_butter), _iref(_i_powdered), _iref(_i_vanilla)],
    component=ComponentId("icing"),
    vessel=_MIXER.id,
)
_frost = Step(
    id=StepId("frost"),
    technique=Plain(kind="frost"),
    label="frost",
    text="Spread the icing over the rolls while they are still just warm.",
    inputs=[_sref(_bake), _sref(_mix_icing)],
    vessel=_PAN.id,
)

FakeRecipe = Recipe(
    id=RecipeId("cinnamon-rolls"),
    slug="cinnamon-rolls",
    title="Ruth's Cinnamon Rolls",
    headnote=(
        "Christmas morning, 1987 onwards. She started the dough the night before "
        "and the house smelled like cinnamon before anyone was allowed downstairs. "
        "The icing goes on while they're still warm — it should melt into the swirls, not sit on top."
    ),
    owner=UserAttribution(user_id=FakeUser.id),
    added_by=FakeUser.id,
    yields=Yield(amount=Amount(value=12), unit="rolls"),
    ingredients=[
        _milk, _yeast, _d_sugar, _d_egg, _d_butter, _d_flour, _d_salt,
        _f_butter, _f_brown, _f_cinnamon,
        _i_cheese, _i_butter, _i_powdered, _i_vanilla,
    ],
    steps=[
        _bloom, _wet, _knead, _proof1,
        _mix_filling,
        _roll, _fill, _shape, _divide, _proof2,
        _preheat, _bake,
        _mix_icing, _frost,
    ],
    components=[_DOUGH, _FILLING, _ICING],
    equipment=[_MIXER, _PAN],
    tags=["brunch", "yeast", "christmas"],
    cuisine="American",
    course=Course.BREAKFAST,
    difficulty=Difficulty.MEDIUM,
    images=[
        Image(
            url="https://images.unsplash.com/photo-1509365465985-25d11c17e812",
            alt="A pan of iced cinnamon rolls",
            caption="Still warm. The icing should gloss, not sit.",
            is_primary=True,
        )
    ],
    notes=[
        Note(
            id="note-second-rise",
            author=FakeUser.id,
            text="Don't skip the second rise. If they look shy in the pan, give them another 15 minutes.",
            created_at=datetime(2024, 12, 24, 8, 15, 0),
        )
    ],
    visibility=Visibility.PUBLIC,
    created_at=datetime(2024, 3, 12, 10, 0, 0),
    updated_at=datetime(2024, 12, 24, 8, 15, 0),
)

# --------------------------------------------------------------------------- #
# Extra recipes so the user page is a list, not a single card
# --------------------------------------------------------------------------- #

_c_butter = _ing("cookie-butter", BUTTER, _qty(1, UnitId.CUP), prep="softened")
_c_sugar = _ing("cookie-sugar", SUGAR, _qty("3/4", UnitId.CUP))
_c_brown = _ing("cookie-brown", BROWN_SUGAR, _qty("3/4", UnitId.CUP), prep="packed")
_c_eggs = _ing("cookie-eggs", EGG, _qty(2))
_c_vanilla = _ing("cookie-vanilla", VANILLA, _qty(1, UnitId.TSP))
_c_flour = _ing("cookie-flour", FLOUR, _qty("2 1/4", UnitId.CUP))
_c_soda = _ing("cookie-soda", BAKING_SODA, _qty(1, UnitId.TSP))
_c_salt = _ing("cookie-salt", SALT, _qty(1, UnitId.TSP))
_c_chips = _ing("cookie-chips", CHOCOLATE, _qty(2, UnitId.CUP), note="or a big handful more")

_SHEET = Equipment(id=EquipmentId("sheet"), name="sheet pan")

_c_preheat = Step(
    id=StepId("cookie-preheat"),
    technique=Preheat(temperature=Temperature(value=375)),
    label="heat the oven to 375°F",
)
_c_cream = Step(
    id=StepId("cookie-cream"),
    technique=Plain(kind="cream"),
    label="cream butter and sugars",
    text="Beat the butter with both sugars until light.",
    inputs=[_iref(_c_butter), _iref(_c_sugar), _iref(_c_brown)],
    duration=Duration(min_minutes=3),
    until="until light",
    vessel=_MIXER.id,
)
_c_wet = Step(
    id=StepId("cookie-wet"),
    technique=Plain(kind="mix"),
    label="beat in eggs",
    text="Beat in the eggs one at a time, then the vanilla.",
    inputs=[_sref(_c_cream), _iref(_c_eggs), _iref(_c_vanilla)],
    vessel=_MIXER.id,
)
_c_dry = Step(
    id=StepId("cookie-dry"),
    technique=Plain(kind="mix"),
    label="add the dry",
    text="Stir in the flour, baking soda, and salt just until you don't see flour.",
    inputs=[_sref(_c_wet), _iref(_c_flour), _iref(_c_soda), _iref(_c_salt)],
    vessel=_MIXER.id,
)
_c_chips_step = Step(
    id=StepId("cookie-fold"),
    technique=Plain(kind="fold"),
    label="fold in chips",
    text="Fold in the 2 cups chocolate chips.",
    inputs=[_sref(_c_dry), _iref(_c_chips)],
)
_c_bake = Step(
    id=StepId("cookie-bake"),
    technique=Bake(temperature=Temperature(value=375), rack="middle"),
    label="bake",
    text="Scoop onto a sheet pan and bake until the edges are set and the centers still look soft.",
    inputs=[_sref(_c_chips_step)],
    duration=Duration(min_minutes=9, max_minutes=11),
    until="until the edges are set",
    vessel=_SHEET.id,
)

FakeCookies = Recipe(
    id=RecipeId("chocolate-chip-cookies"),
    slug="chocolate-chip-cookies",
    title="The Chocolate Chip Cookies",
    headnote="The back-of-the-bag recipe, except she always adds more chips than it says.",
    owner=UserAttribution(user_id=FakeUser.id),
    added_by=FakeUser.id,
    yields=Yield(amount=Amount(value=48), unit="cookies"),
    ingredients=[
        _c_butter, _c_sugar, _c_brown, _c_eggs, _c_vanilla,
        _c_flour, _c_soda, _c_salt, _c_chips,
    ],
    steps=[_c_preheat, _c_cream, _c_wet, _c_dry, _c_chips_step, _c_bake],
    equipment=[_MIXER, _SHEET],
    tags=["cookies", "weeknight"],
    course=Course.DESSERT,
    difficulty=Difficulty.EASY,
    images=[
        Image(
            url="https://images.unsplash.com/photo-1499636136210-6f4ee915583e",
            alt="A pile of chocolate chip cookies",
            is_primary=True,
        )
    ],
    visibility=Visibility.PUBLIC,
    created_at=datetime(2024, 5, 2, 16, 0, 0),
    updated_at=datetime(2024, 5, 2, 16, 0, 0),
)

_t_bread = _ing("toast-bread", BREAD, _qty(1, UnitId.SLICE))
_t_butter = _ing("toast-butter", BUTTER, Quantity(), note="a smear")
_t_sugar = _ing("toast-sugar", SUGAR, Quantity(), note="a sprinkle")
_t_cinnamon = _ing("toast-cinnamon", CINNAMON, Quantity(), note="a sprinkle")

# No step inputs on purpose: the view toggle should hide, not render an empty grid.
FakeToast = Recipe(
    id=RecipeId("cinnamon-toast"),
    slug="cinnamon-toast",
    title="Emergency Cinnamon Toast",
    headnote="For the mornings the rolls did not happen. She never wrote this down; Tucker did.",
    owner=ExternalAttribution(name="Ruth Brewer", source="the way she always made it"),
    added_by=FakeUser.id,
    yields=Yield(amount=Amount(value=1), unit="slice"),
    ingredients=[_t_bread, _t_butter, _t_sugar, _t_cinnamon],
    steps=[
        Step(
            id=StepId("toast"),
            technique=Plain(kind="toast"),
            label="toast the bread",
            text="Toast the bread. Butter it. Sugar and cinnamon on top. That's it.",
        )
    ],
    course=Course.BREAKFAST,
    difficulty=Difficulty.EASY,
    visibility=Visibility.PUBLIC,
    created_at=datetime(2025, 1, 4, 7, 30, 0),
    updated_at=datetime(2025, 1, 4, 7, 30, 0),
)

FakeRecipes: list[Recipe] = [FakeRecipe, FakeCookies, FakeToast]


def dump() -> dict:
    """JSON-ready bundle the frontend can import without talking to an API yet."""

    def recipe_json(recipe: Recipe) -> dict:
        data = recipe.model_dump(mode="json")
        data["total_time_minutes"] = recipe.total_time_minutes
        data["gridable"] = any(step.inputs for step in recipe.steps)
        data["grid_row_order"] = list(recipe.grid_row_order())
        return data

    return {
        "user": FakeUser.model_dump(mode="json"),
        "foods": {f.id: f.model_dump(mode="json") for f in FakeFoods},
        "recipe": recipe_json(FakeRecipe),
        "recipes": [recipe_json(r) for r in FakeRecipes],
    }


if __name__ == "__main__":
    import json
    import sys

    json.dump(dump(), sys.stdout, indent=2)
    sys.stdout.write("\n")
