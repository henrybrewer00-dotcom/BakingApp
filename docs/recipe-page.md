# Recipe Page — Content Inventory

Everything that could live on a single recipe page, grouped by zone. Not a layout.

Each item is marked:

- **[v1]** needed for the first usable version
- **[later]** real, but not day one
- `(have)` the data model already supports it
- `(needs: …)` requires a model addition
- `(ui)` pure presentation, no model impact

The strategic note up front: a generic recipe site is ingredients plus steps. A *family*
recipe site lives on the layer around them — whose recipe it is, the story, who has
cooked it, what Mom changed in 1998. Budget real space for that; it is the reason
someone visits this page instead of Googling the dish.

---

## 1. Header / identity

- **[v1]** Title `(have)`
- **[v1]** Owner — "Grandma Ruth's" with avatar, clickable to their page `(needs: Person entity; today owner is free text)`
- **[v1]** Headnote / story — the paragraph about where this came from `(have)`
- **[v1]** Hero image `(have)`
- **[v1]** Tag badges: course, cuisine, occasion, dietary `(have, except occasion)`
- **[v1]** Added-by line — "added by Tucker, Mar 2024", deliberately smaller than owner `(have)`
- **[later]** Alternate name / a.k.a. — "Sunday Chili" `(needs: subtitle field)`
- **[later]** Image gallery, multiple photos `(have)`
- **[later]** Source line — "from the 1974 church cookbook, p. 34", linked `(have)`
- **[later]** Forked-from — "adapted from Carol's version" `(have)`
- **[later]** Last updated / last cooked `(have updated_at; needs: cook log)`
- **[later]** Visibility indicator `(have)`
- **[later]** Favorite toggle `(needs: per-user favorites)`
- **[later]** Loved-it count — hearts, not 5-star ratings; nobody rates Grandma 3/5 `(needs: reactions)`

## 2. At-a-glance bar

- **[v1]** Total time `(have — sum of step durations)`
- **[v1]** Yield / servings `(have)`
- **[v1]** Difficulty `(have)`
- **[v1]** Oven temperature, surfaced early since you preheat first `(have — read off Bake/Roast/Preheat)`
- **[v1]** Equipment list `(have)`
- **[later]** Prep vs. cook time split — derivable by bucketing technique kinds: knife and
  mixing work is prep, heat and waiting is cook `(have, needs derivation helper)`
- **[later]** Active vs. total time — same trick: Rest, Chill, Proof, Marinate and Cool are
  passive, everything else is active `(have, needs derivation helper)`
- **[later]** Serving size, distinct from yield `(needs: field)`
- **[later]** Nutrition `(needs: a lot; probably never for a family site)`

## 3. Controls

- **[v1]** View mode toggle: classic ↔ grid `(ui)`
- **[v1]** Servings scaler — 0.5x / 1x / 2x or a number input; rewrites every quantity live
  `(have — exact Fractions, so thirds stay thirds)`
- **[v1]** Scaler caveat text — times, pan sizes and oven temps do *not* scale, and the UI
  should say so rather than implying a 2x recipe takes 2x as long `(ui)`
- **[later]** US ↔ metric toggle `(have — base_factor is in the unit registry, unused so far)`
- **[later]** Volume ↔ weight toggle — the one bakers actually want `(needs: density on FoodItem)`
- **[later]** Cook mode entry point `(ui)`

## 4. Ingredients

- **[v1]** Rows: amount, unit, food, prep note, trailing note `(have)`
- **[v1]** Grouped under component headings — "For the dough" / "For the glaze" `(have)`
- **[v1]** Optional marker — visually distinct, not buried in note text `(needs: the optional
  flag we dropped, or accept it renders as plain text)`
- **[v1]** Scaled amounts update in place `(have)`
- **[later]** Tick-off checkboxes with strike-through, persisted per session `(ui)`
- **[later]** Hover an ingredient → highlight the step that uses it, and vice versa. This is
  the payoff of the input graph and it works in *both* view modes `(have)`
- **[later]** Substitutions shown inline `(needs: the substitutions field we dropped, or note text)`
- **[later]** Unscalable rows flagged when scaling — "a big scoop" cannot be doubled `(have — Quantity.scalable)`
- **[later]** Copy all / add to shopping list `(needs: shopping list)`

## 5. Instructions — classic mode

- **[v1]** Numbered steps, grouped by component with subheadings `(have)`
- **[v1]** Per step: prose, duration, doneness cue, heat level, attention note `(have)`
- **[v1]** Ingredient amounts restated inside the step text — "add the 2 cups stock" — so
  nobody scrolls back up mid-cook `(have — generate from step inputs)`
- **[later]** Tap a duration to start a timer `(have — Duration is structured, not prose)`
- **[later]** Step checkboxes / progress `(ui)`
- **[later]** Per-step photos `(needs: image on Step)`
- **[later]** Equipment called out per step `(have — Step.vessel)`
- **[later]** Reserved outputs surfaced — "set aside 1 cup for step 7" `(have — Reserved)`

## 6. Grid mode

- **[v1]** The staircase: ingredient rows left, one column per step, each cell spanning the
  rows it consumes `(have)`
- **[v1]** Full-width banner rows for input-less setup steps `(have — Step.is_banner)`
- **[v1]** Graceful absence — most recipes will not be decomposed, so the toggle must hide
  itself rather than render a broken grid `(needs: a gridable property)`
- **[v1]** Mobile answer. This layout is inherently wide and phones are where people cook.
  Decide early whether it degrades to classic, scrolls horizontally, or rotates
  — this is the biggest open risk on the page `(ui)`
- **[later]** Component swimlanes — one staircase per component, merging at assembly `(have)`
- **[later]** Per-cell detail on tap `(ui)`
- **[later]** Print-friendly rendering — this view is genuinely nice on paper `(ui)`

## 7. Cook mode

- **[later]** Screen wake lock `(ui)`
- **[later]** Large type, one step at a time `(ui)`
- **[later]** Running timers with alerts `(have)`
- **[later]** Ingredients pinned or recallable without losing your place `(ui)`

## 8. Notes and the family layer

- **[v1]** Notes / comments with author and date `(have — Note)`
- **[v1]** Distinction between the headnote (the story, top of page) and notes (added
  after, near the bottom) `(have)`
- **[later]** Threaded replies `(needs: parent_id)`
- **[later]** Private notes vs. shared `(needs: flag)`
- **[later]** Step-level notes as opposed to recipe-level `(needs: link)`
- **[later]** "I made this" log — who cooked it, when, how it went `(needs: cook log)`
- **[later]** Version history — "Mom changed the sugar to 3/4 cup in 2019". Unusually
  valuable for a family archive `(needs: revisions)`
- **[later]** Photos from family members who cooked it, distinct from the hero image `(needs: user photos)`

## 9. Related and navigation

- **[v1]** More from this person `(needs: Person entity)`
- **[later]** Sub-recipe links — "uses Grandma's pie crust" as a real reference, not prose
  `(needs: a step or component that can point at another Recipe)`
- **[later]** Reverse links — "this crust is used in 4 pies" `(needs: same)`
- **[later]** Similar recipes by shared tags `(have)`
- **[later]** Previous / next within a collection `(needs: collections)`

## 10. Actions

- **[v1]** Print — a real print stylesheet, not the screen layout. Family cooks print. `(ui)`
- **[v1]** Share link `(ui)`
- **[v1]** Edit, when permitted `(have)`
- **[later]** Fork — "make my version" `(have — forked_from)`
- **[later]** Export to PDF or plain text `(ui)`
- **[later]** Add to shopping list / meal plan `(needs: both)`
- **[later]** Archive or delete `(needs: soft-delete)`
- **[later]** Suggest a correction, for recipes you do not own `(needs: suggestions)`

## 11. Empty and edge states

Worth mocking explicitly — they are most of what the page actually looks like early on.

- **[v1]** No image
- **[v1]** No times anywhere — "cook until done" recipes
- **[v1]** Not gridable, so no view toggle
- **[v1]** No components, so no ingredient subheadings
- **[v1]** No notes yet
- **[v1]** Unscalable quantities while scaled
- **[later]** Very long ingredient lists — 30+ rows breaks the grid's row-height assumptions
- **[later]** Single-step recipes
- **[later]** Recipes with a component but only one step in it

## 12. Gaps this page opens in the model

Ordered by how much the page needs them.

1. **`Person` as a first-class entity.** "More from this person" and clickable owner
   attribution both need it, and free-text owner names will fork Grandma into two people.
2. **A `gridable` property on Recipe.** The view toggle needs to know whether the steps
   declare inputs; today it would render a meaningless grid.
3. **Sub-recipe references.** A step or component that points at another `Recipe`. Family
   recipes cross-reference constantly and there is currently no way to express it.
4. **Derivation helpers** for prep/cook and active/total time, bucketing technique kinds.
5. **Per-step images** — a field on `Step`.
6. **Cook log, reactions, favorites** — the whole "who has made this" layer, all new.
7. **Occasion tag** — Thanksgiving, Christmas Eve. How families actually reach for recipes.
8. **Revisions** — if version history matters, it is much cheaper to design in now.

Three fields we removed earlier show up here: `optional` on ingredients (§4), `density`
for the weight toggle (§3), and `substitutions` (§4). All are additive whenever you want
them; none block a mock.
