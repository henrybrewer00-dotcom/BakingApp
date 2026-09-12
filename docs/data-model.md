# Recipe Data Model

Python (Pydantic v2) is the source of truth. TypeScript types for the React app
are generated from `Recipe.model_json_schema()`.

## 1. The decision that shapes everything

The grid is only renderable if **each step knows which ingredients it consumes**.
In the reference image, "cook onion" spans exactly two ingredient rows (olive
oil, yellow onion); "toast spices" spans the next four; each later step's cell
starts where the previous one ended and inherits everything before it.

A recipe is not a list of ingredients plus a list of instructions. It is a
**DAG**: steps take inputs (ingredients and/or the output of earlier steps) and
produce an intermediate that later steps consume.

- The classic frontend is a *projection* of the DAG (topological order, rendered as prose).
- The grid frontend is the DAG rendered directly.

Adding the input links now is cheap. Retrofitting them later means re-entering
every recipe — the ingredient→step mapping cannot be recovered from prose.

## 2. Module layout

```
backend/recipes/models/
    common.py      ids, Amount, UnitId, Quantity, Duration, Temperature, HeatLevel
    user.py        User, Attribution
    food.py        FoodItem, RecipeIngredient
    technique.py   Technique discriminated union
    step.py        Step, StepInput, Portion, Reserved, Equipment
    recipe.py      Recipe, Yield, Component
```

## 3. Identity and provenance

Whose recipe it is is often not a site user (Grandma, a cookbook, NYT Cooking).
Who typed it in always is.

```python
class User(Base):
    id: UserId
    display_name: str
    email: EmailStr
    created_at: datetime

class UserAttribution(Base):
    kind: Literal["user"] = "user"
    user_id: UserId

class ExternalAttribution(Base):
    kind: Literal["external"] = "external"
    name: str                      # "Alison Roman", "Grandma Ruth"
    source: str | None = None
    url: HttpUrl | None = None
    page: str | None = None

Attribution = Annotated[UserAttribution | ExternalAttribution,
                        Field(discriminator="kind")]
```

`Recipe.owner: Attribution` vs. `Recipe.added_by: UserId`. Also
`forked_from: RecipeId | None` for lineage.

## 4. Quantities

Recipes contain `1/4 cup`, `1 1/2 tsp`, `2 cans … 15 oz each`, `4 cloves`,
`1 large`, and `yogurt and pita` with no quantity at all. Also `5–6 min` ranges.

```python
class Amount(Base):
    value: Fraction                # exact rational: 1/3 * 3 == 1
    upper: Fraction | None = None  # "2-3 cloves"
    approximate: bool = False      # "a pinch", "to taste"

class Quantity(Base):
    amount: Amount | None = None   # None = "yogurt and pita — to serve"
    unit: UnitId | None = None     # None = bare count: "1 large yellow onion"
    size: str | None = None        # "large", "15 oz each"
```

`UnitId` is a closed editor vocabulary (`tsp`, `cup`, `clove`, …). Conversion
(cup → ml) is Pint's job when we need it — there is no parallel factor table.
`size` is free text: "large onion" is not a real unit.

Amounts serialize as `"3/2"` on the wire and render as `"1 1/2"` on a card.
`fractions.Fraction` parses `"3/2"` and `1.5`; mixed numbers (`"1 1/2"`) are
the only recipe-specific case.

## 5. Ingredients — two classes

```python
class FoodItem(Base):
    """The canonical thing, shared across all recipes."""
    id: FoodId
    name: str
    plural_name: str
    category: FoodCategory
    allergens: list[Allergen]
    dietary_tags: list[DietaryTag]
    default_unit: UnitId | None

class RecipeIngredient(Base):
    """This recipe's use of a FoodItem — the left-hand rows in the grid."""
    id: IngredientId
    food: FoodId
    quantity: Quantity
    prep: str | None = None        # "finely chopped"
    note: str | None = None        # "optional", "or cilantro"
    component: ComponentId | None = None
    display_order: int | None = None
```

The split is what makes shopping lists, search, and allergen filters possible.
Everything after the em-dash on a card maps to `prep` or `note`, which is what
keeps the food name joinable across recipes.

## 6. Techniques

A tagged union so React gets exhaustive `switch` on `kind`. A subclass exists
only when it carries data; fieldless verbs share `Plain`. Duration, heat, and
doneness live on `Step` — they apply to almost every technique, and putting
them on each variant would make "total time" a union-match.

```python
class Plain(BaseTechnique):
    kind: Literal["chop", "mince", "mix", "combine", "stir", "whisk",
                  "fold", "cream", "sift", "toast", "boil", "steam",
                  "season", "assemble", "frost", "garnish", "serve",
                  "peel", "zest", "setup"]

class Dice(BaseTechnique):
    kind: Literal["dice"] = "dice"
    size: Literal["fine", "medium", "large"] | None = None

class Bake(BaseTechnique):
    kind: Literal["bake"] = "bake"
    temperature: Temperature       # required: a bake without a temp is not a bake
    rack: RackPosition | None = None
    convection: bool = False
    covered: bool | None = None

class Custom(BaseTechnique):
    kind: Literal["custom"] = "custom"
    verb: str                      # escape hatch — always keep this

Technique = Annotated[Plain | Dice | Bake | … | Custom, Field(discriminator="kind")]
```

Other subclasses (only because they have fields): `Slice`, `Grate`, `Roll`,
`Shape`, `Divide`, `Whip`, `Knead`, `Saute`, `Fry`, `Simmer`, `Melt`, `Reduce`,
`Roast`, `Broil`, `Grill`, `Rest`, `Chill`, `Cool`, `Proof`, `Marinate`,
`Preheat`.

A setup banner is `Plain(kind="setup")` with no inputs, a vessel, and a heat
level. Zero-input steps render full-width, so it falls out of the model.

## 7. Steps

```python
class Portion(Base):
    fraction: Fraction | None = None
    quantity: Quantity | None = None
    note: str | None = None

class IngredientRef(Base):
    ref: Literal["ingredient"] = "ingredient"
    ingredient_id: IngredientId
    portion: Portion | None = None  # None = all of it

class StepRef(Base):
    ref: Literal["step"] = "step"
    step_id: StepId
    output_id: OutputId | None = None
    portion: Portion | None = None

StepInput = Annotated[IngredientRef | StepRef, Field(discriminator="ref")]

class Reserved(Base):
    id: OutputId
    name: str
    quantity: Quantity | None = None

class Step(Base):
    id: StepId
    technique: Technique
    inputs: list[StepInput]        # <- what makes the grid renderable
    label: str                     # "cook onion"
    text: str | None = None        # prose override; otherwise generated
    duration: Duration | None = None
    until: str | None = None       # "until golden"
    heat: HeatLevel | None = None
    attention: str | None = None
    vessel: EquipmentId | None = None
    reserves: list[Reserved] = []
    component: ComponentId | None = None
    order: int | None = None       # Recipe fills it from list order
```

A step's **primary** output is implicit (its own `id`). `reserves` covers
"set some aside". A list of outputs on every step would make the common
single-output case noisier.

```python
class Equipment(Base):
    id: EquipmentId
    name: str                      # "Dutch oven", "sheet pan"
    size: str | None = None
```

## 8. Components

A named sub-assembly (the dough, the glaze). Enum plus free `name`, not a
`Dough` subclass — the fields do not differ, only the label.

```python
class Component(Base):
    id: ComponentId
    name: str                      # "Brioche dough", "Lemon glaze"
    kind: ComponentKind            # dough, batter, filling, frosting, …
    order: int | None = None
```

Ingredients and steps point at it by id rather than nesting inside it, so an
assembly step can consume the dough *and* the filling. Each component is a
sub-DAG; the grid draws one staircase per component and merges at assembly.

## 9. Recipe

```python
class Yield(Base):
    amount: Amount
    unit: str                      # "servings", "cookies", "loaf"

class Recipe(Base):
    id: RecipeId
    slug: str
    title: str
    headnote: str | None = None
    owner: Attribution
    added_by: UserId
    yields: Yield | None = None
    ingredients: list[RecipeIngredient]
    steps: list[Step]
    components: list[Component] = []
    equipment: list[Equipment] = []
    tags: list[str] = []
    cuisine: str | None = None
    course: Course | None = None
    difficulty: Difficulty | None = None
    images: list[Image] = []
    notes: list[Note] = []
    source_url: HttpUrl | None = None
    forked_from: RecipeId | None = None
    visibility: Visibility = Visibility.PRIVATE
    created_at: datetime
    updated_at: datetime
```

Derived, not stored: `total_time_minutes` (sum of step durations),
`grid_row_order` (ingredient order that makes each step's inputs a contiguous
block). Allergen and dietary tags live on `FoodItem` and are joined at query
time, not cached on the recipe.

## 10. Validation

Hard errors — the data is incoherent:

1. Duplicate ingredient / step / component / equipment / output ids.
2. Every `IngredientRef`, `StepRef`, component, vessel, and technique `fat`
   resolves.
3. Step orders are distinct, and every step comes after the steps it consumes
   (acyclicity).
4. `Bake` requires a temperature; ranged amounts satisfy `upper > value`.

Soft checks — a half-entered editor recipe must still be a valid object:

- `unused_ingredients()` — usually a mistake, sometimes a garnish.
- `terminal_steps()` — a finished recipe has exactly one.

`Recipe.scaled(n)` multiplies amounts with exact rationals, so thirds stay thirds.

## 11. Rendering

**Classic view.** Ingredients sectioned by `component` and ordered by
`display_order`; steps in `order`, rendered from `text` or
`label + duration + until`.

**Grid view.** Columns = steps in order. Rows = `grid_row_order()`. Each cell
spans from its first to its last input row and inherits everything above.
Contiguity holds within a single chain; two components in parallel are two
staircases that merge at the assembly step.

## 12. Python / TypeScript

`Recipe.model_json_schema()` → `json-schema-to-typescript` as a build step.
`Literal` discriminators become TS discriminated unions. `Fraction` is a
string on the wire (`"3/2"`); `format_amount` is the display form (`"1 1/2"`).
