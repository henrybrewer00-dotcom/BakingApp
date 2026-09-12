from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .common import Base, IngredientId, Temperature

# Techniques with no extra fields share one class. A subclass earns its keep
# only when it carries data (temperature, fat, location, …).


class BaseTechnique(Base):
    kind: str

    @property
    def display_verb(self) -> str:
        if self.kind == "setup":
            return "set"
        return self.kind.replace("_", " ")


class Plain(BaseTechnique):
    kind: Literal[
        "chop",
        "mince",
        "peel",
        "zest",
        "mix",
        "combine",
        "stir",
        "whisk",
        "fold",
        "cream",
        "sift",
        "toast",
        "boil",
        "steam",
        "season",
        "assemble",
        "frost",
        "garnish",
        "serve",
        "setup",
    ]


class Dice(BaseTechnique):
    kind: Literal["dice"] = "dice"
    size: Literal["fine", "medium", "large"] | None = None


class Slice(BaseTechnique):
    kind: Literal["slice"] = "slice"
    thickness: str | None = None


class Grate(BaseTechnique):
    kind: Literal["grate"] = "grate"
    size: Literal["fine", "coarse"] | None = None


class Roll(BaseTechnique):
    kind: Literal["roll"] = "roll"
    thickness: str | None = None


class Shape(BaseTechnique):
    kind: Literal["shape"] = "shape"
    form: str | None = None


class Divide(BaseTechnique):
    kind: Literal["divide"] = "divide"
    portions: int | None = Field(default=None, ge=2)


class Whip(BaseTechnique):
    kind: Literal["whip"] = "whip"
    peaks: Literal["soft", "medium", "stiff"] | None = None


class Knead(BaseTechnique):
    kind: Literal["knead"] = "knead"
    method: Literal["hand", "stand_mixer", "food_processor"] | None = None


class Saute(BaseTechnique):
    kind: Literal["saute"] = "saute"
    fat: IngredientId | None = None


class Fry(BaseTechnique):
    kind: Literal["fry"] = "fry"
    fat: IngredientId | None = None
    style: Literal["shallow", "deep", "pan"] | None = None


class Simmer(BaseTechnique):
    kind: Literal["simmer"] = "simmer"
    covered: bool = False


class Melt(BaseTechnique):
    kind: Literal["melt"] = "melt"
    method: Literal["direct", "double_boiler", "microwave"] | None = None


class Reduce(BaseTechnique):
    kind: Literal["reduce"] = "reduce"
    to: str | None = None


RackPosition = Literal["top", "upper_middle", "middle", "lower_middle", "bottom"]


class Bake(BaseTechnique):
    kind: Literal["bake"] = "bake"
    temperature: Temperature
    rack: RackPosition | None = None
    convection: bool = False
    covered: bool | None = None


class Roast(BaseTechnique):
    kind: Literal["roast"] = "roast"
    temperature: Temperature
    rack: RackPosition | None = None
    convection: bool = False


class Broil(BaseTechnique):
    kind: Literal["broil"] = "broil"
    rack: RackPosition | None = None


class Grill(BaseTechnique):
    kind: Literal["grill"] = "grill"
    zone: Literal["direct", "indirect"] | None = None


class Rest(BaseTechnique):
    kind: Literal["rest"] = "rest"
    location: Literal["counter", "fridge", "freezer"] = "counter"


class Chill(BaseTechnique):
    kind: Literal["chill"] = "chill"
    location: Literal["fridge", "freezer"] = "fridge"


class Cool(BaseTechnique):
    kind: Literal["cool"] = "cool"
    location: Literal["pan", "rack", "counter"] | None = None


class Proof(BaseTechnique):
    kind: Literal["proof"] = "proof"
    covered: bool = True


class Marinate(BaseTechnique):
    kind: Literal["marinate"] = "marinate"
    location: Literal["counter", "fridge"] = "fridge"


class Preheat(BaseTechnique):
    kind: Literal["preheat"] = "preheat"
    temperature: Temperature | None = None


class Custom(BaseTechnique):
    """Escape hatch so the taxonomy never blocks data entry."""

    kind: Literal["custom"] = "custom"
    verb: str

    @property
    def display_verb(self) -> str:
        return self.verb


Technique = Annotated[
    Plain
    | Dice
    | Slice
    | Grate
    | Roll
    | Shape
    | Divide
    | Whip
    | Knead
    | Saute
    | Fry
    | Simmer
    | Melt
    | Reduce
    | Bake
    | Roast
    | Broil
    | Grill
    | Rest
    | Chill
    | Cool
    | Proof
    | Marinate
    | Preheat
    | Custom,
    Field(discriminator="kind"),
]
