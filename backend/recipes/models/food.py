from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from .common import Base, ComponentId, FoodId, IngredientId, Quantity, UnitId, new_id


class FoodCategory(StrEnum):
    PRODUCE = "produce"
    PROTEIN = "protein"
    DAIRY = "dairy"
    EGG = "egg"
    GRAIN = "grain"
    FLOUR = "flour"
    SUGAR = "sugar"
    FAT = "fat"
    SPICE = "spice"
    HERB = "herb"
    CONDIMENT = "condiment"
    LEAVENER = "leavener"
    NUT = "nut"
    LEGUME = "legume"
    CANNED = "canned"
    LIQUID = "liquid"
    ALCOHOL = "alcohol"
    OTHER = "other"


class Allergen(StrEnum):
    MILK = "milk"
    EGG = "egg"
    FISH = "fish"
    SHELLFISH = "shellfish"
    TREE_NUT = "tree_nut"
    PEANUT = "peanut"
    WHEAT = "wheat"
    SOY = "soy"
    SESAME = "sesame"
    GLUTEN = "gluten"


class DietaryTag(StrEnum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    KOSHER = "kosher"
    HALAL = "halal"


class FoodItem(Base):
    id: FoodId = Field(default_factory=lambda: FoodId(new_id()))
    name: str  # "yellow onion"
    plural_name: str  # "yellow onions"
    category: FoodCategory = FoodCategory.OTHER
    allergens: list[Allergen] = Field(default_factory=list)
    dietary_tags: list[DietaryTag] = Field(default_factory=list)
    default_unit: UnitId | None = None


class RecipeIngredient(Base):
    id: IngredientId = Field(default_factory=lambda: IngredientId(new_id()))
    food: FoodId
    quantity: Quantity = Field(default_factory=Quantity)
    prep: str | None = None 
    note: str | None = None 
    component: ComponentId | None = None
    display_order: int | None = None
