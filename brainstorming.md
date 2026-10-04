# Kaggriculture — Business Experts Brainstorming

> **Estado del documento:** documento histórico de ideación y contexto arquitectónico. No es una especificación de implementación. Para features de `SemanticState`, consultar `Semantic contract.md`; para patrones no validados, consultar `Semantic pattern.md`.

## Estado actual (2026-10-04)

Implementados: `FinancialExpert`, `AgricultureExpert`, `InventoryExpert`, `LivestockExpert`, `MarketExpert` y `OpponentExpert` (seis Business Experts). `SemanticState` está implementado con 14 features semánticas (8 situaciones, 3 relaciones y 3 riesgos); las cuatro categorías `risks`, `opportunities`, `situations` y `relationships` están presentes. La lista exacta y su contrato vigente están en `Semantic contract.md`. `opportunities` está vacío actualmente.

`OperationsExpert`, `ProductionExpert`, `StrategicExpert`, `StateTransition`, reward, credit assignment, Decision Experts y Coordinator no están implementados. La existencia de `StrategicExpert` está decidida a nivel arquitectónico; su interfaz y fuentes siguen abiertas. Las listas de features de este documento son ideas, salvo que se confirmen en el código y en el contrato semántico.

## 1. Objective

The objective is to transform the raw Kaggriculture game observation (`obs`) into meaningful business-domain information that can later be used by decision-making, Machine Learning and Reinforcement Learning models.

The architecture is based on a set of specialized **Business Experts**.

Each Expert is responsible for one specific business domain.

The first layer is deliberately deterministic:

```text
RAW OBSERVATION
       ↓
Business Domain Experts
       ↓
Domain facts
    ↓
SemanticState
  ├── situations
  ├── relationships
  ├── risks
  └── opportunities
       ↓
Model-specific features
    ↓
Specialized Decision Experts
    ↓
Decision Coordinator
       ↓
ACTION
```

The Business Experts do **not** make strategic decisions.

Their purpose is to correctly describe the current state of the game from different business perspectives.

---

# 2. Architecture

```text
                            OBS
                             │
                 ┌─────────────────┼──────────────────────────┐
                 │                 │                          │
                 ▼                 ▼                          ▼
             FinancialExpert   AgricultureExpert           LivestockExpert
             InventoryExpert   MarketExpert                OpponentExpert
                 └─────────────────┼──────────────────────────┘
                             ↓
                        Domain facts
                             ↓
                          SemanticState
                  (situations / relationships / risks /
                       opportunities)
                             ↓
                    Model-specific features
                             ↓
                    Decision Experts + Coordinator
                             ↓
                           ACTION
```

Cross-domain semantic features belong inside `SemanticState`; a separate mandatory `Cross-Domain Synthetic Features` layer is not part of the current architecture. The eventual role of `ProductionExpert` remains future design, not an implemented integration stage.

---

# 3. Architectural Principles

The architecture follows these principles:

* `obs` is the **source of truth**.
* Every feature has one logical owner.
* Every Expert has a clearly defined business responsibility.
* Experts may consume information from other Experts when necessary.
* An Expert must not modify another Expert's internal state.
* Each Expert exposes information through a public interface.
* `get_features()` exposes the complete public feature set.
* Individual `get_*()` methods expose specific values.
* Internal implementation details remain encapsulated.
* The deterministic Business Expert layer does not make strategic decisions.
* Predictive, optimization and ML logic belongs to later layers.
* Historical state is maintained only by Experts that explicitly require temporal information.
* Current state must not be confused with prediction.
* Economic value must not be confused with physical inventory.
* Operational state must not be confused with financial state.
* Production facts must not be duplicated across multiple Experts.

---

# 4. Business Experts

The current implementation contains six Business Experts:

1. `FinancialExpert`
2. `AgricultureExpert`
3. `LivestockExpert`
4. `InventoryExpert`
5. `MarketExpert`
6. `OpponentExpert`

Current and planned status:

```text
┌──────────────────────┬──────────────┐
│ Expert               │ Status       │
├──────────────────────┼──────────────┤
│ FinancialExpert      │ DONE         │
│ AgricultureExpert    │ DONE         │
│ LivestockExpert      │ DONE         │
│ InventoryExpert      │ DONE         │
│ MarketExpert         │ DONE         │
│ OpponentExpert       │ DONE         │
│ OperationsExpert     │ PLANNED      │
│ ProductionExpert     │ PLANNED      │
│ StrategicExpert      │ DESIGNED     │
└──────────────────────┴──────────────┘
```

`StrategicExpert` is a decided future component, not part of the six implemented experts. Its data sources and interface remain open. Operations and Production are also not implemented; their inclusion and boundaries must not be inferred from this historical brainstorming document.

However, completing the remaining Experts is **not automatically the next step**.

Before adding more domain logic, the existing deterministic layer should be integrated and validated through a common semantic state.

---

# 5. FinancialExpert

## Status

**Implemented**

## Responsibility

`FinancialExpert` represents the economic and financial situation of one player.

It is responsible for:

* cash
* income
* expenses
* cash flow
* inventory valuation
* seed valuation
* animal asset valuation
* land acquisition value
* assets
* net worth
* liquidity
* investments
* acquisition costs
* aggregate investment return
* payback

It does not own:

* physical inventory state
* detailed livestock state
* agricultural state
* market state
* operational state

---

## 5.1 Autonomy

`FinancialExpert` is deliberately autonomous.

It obtains financial information directly from:

```text
obs
├── farms[player]
├── private
└── market
```

This allows the financial state to be reconstructed without depending on another Expert's interpretation.

It may use raw observation information to calculate financial values such as the economic value of animals or inventory.

---

## 5.2 Financial features

### Time

* `step`
* `day`
* `hour`
* `days_remaining`
* `steps_remaining`
* `season_progress`
* `is_last_day`
* `is_last_week`
* `is_day_start`
* `is_day_end`

### Cash and financial flows

* `cash`
* `income`
* `expenses`
* `cash_flow`

### Economic valuation

* `inventory_value`
* `seed_value`
* `animal_asset_value`
* `land_value`

### Financial position

* `assets`
* `net_worth`
* `balance`
* `liquidity_ratio`
* `money_per_day_remaining`

`money_per_day_remaining` is a planning indicator and not an accounting measure.

---

## 5.3 Animal financial representation

Animals are economic assets.

`FinancialExpert` only needs the current animal population to calculate their economic value.

The detailed animal state belongs to `LivestockExpert`.

Current acquisition values:

```text
GOOSE  = $300
COW    = $400
SHEEP  = $500
```

Therefore:

```text
animal_asset_value =
      GOOSE × 300
    + COW × 400
    + SHEEP × 500
```

Animals must be counted whether they are:

* placed on the farm
* stored in the shed
* carried by the farmer
* carried by a farm hand

---

## 5.4 Land valuation

Land is currently valued using historical/acquisition cost.

The initial `NW` quadrant has no additional acquisition cost.

Additional quadrants have cumulative acquisition values:

| Unlocked quadrants         | Acquisition value |
| -------------------------- | ----------------: |
| `["NW"]`                   |              `$0` |
| `["NW", "NE"]`             |          `$1,000` |
| `["NW", "NE", "SW"]`       |          `$3,000` |
| `["NW", "NE", "SW", "SE"]` |          `$7,000` |

Therefore:

```text
NW
└── $0

NW + 1 additional quadrant
└── $1,000

NW + 2 additional quadrants
└── $3,000

NW + 3 additional quadrants
└── $7,000
```

`land_value` represents historical/acquisition value.

It does not represent predicted resale value or speculative future appreciation.

---

## 5.5 Net worth

Currently there are no explicit liabilities modeled.

Therefore:

```text
assets =
    inventory_value
    + seed_value
    + animal_asset_value
    + land_value
```

and:

```text
net_worth =
    cash + assets
```

Currently:

```text
balance = net_worth
```

---

## 5.6 Liquidity

```text
liquidity_ratio =
    cash / net_worth
```

This represents the proportion of total financial value currently held as cash.

---

## 5.7 Transactions

A fundamental distinction is made between **cash movement** and **economic result**.

For example:

```text
BUY_ANIMAL COW 1
```

causes:

```text
cash          ↓
animal asset  ↑
```

The reduction in cash is therefore not automatically a financial loss.

Relevant transaction categories include:

* `BUY_SEED`
* `BUY_PRODUCT`
* `BUY_ANIMAL`
* `SELL`
* `HIRE`
* `BUY_LAND`
* `BUILD_COOP`
* `BUILD_PASTURE`

Asset acquisition and operating expenses must remain conceptually distinct.

---

## 5.8 Observation without action

The current financial state can be calculated from:

```python
financial.process_observation(obs)
```

However, an isolated observation cannot always reconstruct historical income and expenses.

When action history is unavailable, observed cash variation may be represented as:

```text
cash_flow =
    current_cash - previous_cash
```

The system does not invent an income/expense classification when the observation does not provide enough information.

---

## 5.9 Investment return

`investment_return` currently represents an **aggregate financial result**.

It is deliberately not individual ROI.

The deterministic layer does not calculate:

```text
ROI of one cow
ROI of one sheep
ROI of one goose
ROI of one pasture
ROI of one coop
ROI of one land quadrant
```

Individual attribution requires linking specific investments to subsequent economic consequences.

That belongs to a later analytical layer.

---

## 5.10 Payback

Current payback is aggregate:

```text
payback =
    acquisition_cost / investment_return
```

when the return is positive.

It is not individual asset payback.

---

# 6. AgricultureExpert

## Status

**Implemented**

## Responsibility

`AgricultureExpert` owns the current agricultural state of the player's farm.

It describes:

* farm surface
* crops
* crop state
* watering
* fertilization
* current agricultural production state

It does not decide what to plant, harvest or sell.

---

## 6.1 Temporal state

* `step`
* `day`
* `hour`

---

## 6.2 Farm surface

* total tiles
* locked tiles
* unlocked tiles
* empty tiles
* occupied tiles
* agricultural surface
* occupied crop surface
* free agricultural surface
* weed surface

---

## 6.3 Crop state

For every plant:

* crop type
* planted day
* crop age
* yield units
* watered today
* consecutive unwatered
* fertilized
* fertilized until day
* maximum lifespan
* steps remaining
* ready state

---

## 6.4 Crop aggregation

The Expert aggregates crop information by type:

```text
WHEAT
CARROT
TOMATO
STRAWBERRY
MELON
```

It can expose:

* number of plants
* ready plants
* unwatered plants
* fertilized plants
* current yield
* production ready now

---

## 6.5 Production boundary

`AgricultureExpert` owns the **agricultural production facts**.

It does not attempt to calculate complete farm production.

For example:

```text
AgricultureExpert
    ↓
crop production state
```

while:

```text
ProductionExpert
    ↓
integrated farm production
```

This prevents duplication between crop and livestock production logic.

---

# 7. LivestockExpert

## Status

**Implemented**

## Responsibility

`LivestockExpert` owns the current operational and productive state of livestock.

It answers:

> What animals currently exist, where are they, and what is their current state?

It does not:

* buy animals
* sell animals
* feed animals
* care for animals
* decide where to place animals
* calculate financial profitability
* calculate ROI
* optimize livestock strategy
* calculate reward

---

# 7.1 Source of truth

Actual Kaggriculture observations confirmed that placed animals are explicitly represented on farm tiles.

Example:

```python
{
    'kind': 'PASTURE',
    'animal': 'COW',
    'placed_day': 12,
    'yield_units': 0,
    'consecutive_unfed': 1,
    'fed_today': False,
    'cared_today': False,
    'fertilizer_available': True,
    'pending_care_bonus': 0
}
```

Therefore:

```python
tile["animal"]
```

is the source of truth for an animal currently placed on the farm.

No historical action tracker is required to reconstruct the current placed-animal state.

---

# 7.2 Animal locations

Animals can exist in three relevant states:

```text
                    ANIMAL
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     Placed           Shed          Carried
     on farm                        inventory
```

### Placed animals

Detected by scanning:

```python
me["tiles"]
```

and checking the animal information on the tile.

### Shed animals

Detected through:

```python
private["shed"]
```

### Carried animals

Detected through:

```python
private["inventories"]
```

---

# 7.3 Animal population

The Expert maintains:

```text
placed_animals
shed_animals
carried_animals
animals
total_animals
```

For each species:

```text
GOOSE
COW
SHEEP
```

The total population is:

```text
animals =
    placed_animals
    + shed_animals
    + carried_animals
```

Example:

```text
Placed:
    COW = 1

Carried:
    COW = 1

Shed:
    COW = 0

Total:
    COW = 2
```

---

# 7.4 Individual animal state

For placed animals, `LivestockExpert` exposes:

* animal type
* location
* x
* y
* placed day
* age in days
* yield units
* consecutive unfed days
* fed today
* needs feed
* cared today
* fertilizer available
* pending care bonus

Example:

```python
{
    'animal': 'COW',
    'location': 'PASTURE',
    'x': 4,
    'y': 4,
    'placed_day': 12,
    'age_days': 1,
    'yield_units': 0,
    'consecutive_unfed': 1,
    'fed_today': False,
    'needs_feed': True,
    'cared_today': False,
    'fertilizer_available': True,
    'pending_care_bonus': 0
}
```

---

# 7.5 Feeding state

The `needs_feed` feature was added after validating real game observations.

For a placed animal:

```python
needs_feed = not fed_today
```

This is a **current-state feature**, not a decision.

A real observation demonstrated:

```text
consecutive_unfed = 1
fed_today = False
needs_feed = True
```

The animal was still present during the final steps of day 13.

At the transition to day 14 the animal disappeared.

This confirms that feeding state is an operationally important livestock feature and must be exposed to higher layers.

`LivestockExpert` identifies the condition.

It does not decide how to resolve it.

---

# 7.6 Livestock features

Current public state includes:

### Population

* `animals`
* `placed_animals`
* `shed_animals`
* `carried_animals`
* `total_animals`

### Detailed state

* `animal_details`

From this state, later cross-domain features can be derived, such as:

* number of animals needing feed
* number of animals with consecutive unfed days
* number of animals ready to produce
* total animal yield
* available fertilizer
* animal production capacity

These derived features should be added only after the underlying game rules are verified.

---

# 8. InventoryExpert

## Status

**Implemented**

## Responsibility

`InventoryExpert` owns the current **physical inventory state**.

It answers:

> What physical resources does the player currently have and where are they?

It does not:

* calculate economic value
* decide what to buy
* decide what to sell
* calculate production
* calculate profitability

---

# 8.1 Inventory domains

```text
                    INVENTORY
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
        Seeds          Shed        Carried
```

### Seeds

Obtained from:

```python
private["seeds"]
```

Seeds are a separate inventory category and are not part of shed capacity.

### Shed

Obtained from:

```python
private["shed"]
```

### Carried inventories

Obtained from:

```python
private["inventories"]
```

These represent items carried by the farmer and farm hands.

---

# 8.2 Shed capacity

Current shed capacity:

```text
100 items
```

Seeds are excluded from this capacity.

The Expert therefore exposes:

* shed capacity
* used capacity
* available capacity
* utilization

---

# 8.3 Physical inventory features

Current state includes:

* seeds
* shed
* farmer inventory
* farm-hand inventories
* carried inventory
* total physical inventory
* shed capacity
* used capacity
* available capacity
* utilization

Placed animals are not part of the physical inventory state.

They belong to `LivestockExpert`.

---

# 8.4 Architectural distinction

```text
InventoryExpert
    └── What do I physically have?

FinancialExpert
    └── What is it worth?

LivestockExpert
    └── What is the operational state of my animals?
```

---

# 9. MarketExpert

## Status

**Implemented**

## Responsibility

`MarketExpert` owns and analyzes the current external market state.

It answers:

> What is happening in the market right now?

It does not decide what the player should buy or sell.

---

# 9.1 Current market state

The Expert processes:

* market inventory
* current prices
* product availability
* market equilibrium
* shops
* shop demand context

---

# 9.2 Fixed acquisition prices

The Expert also exposes deterministic acquisition prices that belong to the game economy:

### Seeds

```text
WHEAT       = $10
CARROT      = $20
TOMATO      = $50
STRAWBERRY  = $100
MELON       = $80
```

### Animals

```text
GOOSE  = $300
COW    = $400
SHEEP  = $500
```

### Land

```text
1st additional quadrant = $1,000
2nd additional quadrant = $2,000
3rd additional quadrant = $4,000
```

These are acquisition rules, not dynamic market prices.

---

# 9.3 Market dynamics

The Expert currently calculates deterministic market-state features including:

* price change
* price percentage change
* price trend
* price trend strength
* inventory change
* inventory percentage change
* inventory trend
* inventory trend strength
* equilibrium deviation
* equilibrium position
* market pressure

These are based on observed market states.

They describe what has happened in the market.

They do not constitute future price prediction.

---

# 9.4 Farm-hand hiring cost

The cost of hiring farm hands follows the deterministic daily Fibonacci sequence:

```text
1st hand → 1
2nd hand → 1
3rd hand → 2
4th hand → 3
5th hand → 5
6th hand → 8
...
```

The sequence resets each day.

`MarketExpert` exposes the deterministic cost function.

`OperationsExpert` will represent the resulting operational capacity.

`FinancialExpert` will represent the corresponding financial expense when applicable.

---

# 9.5 Market versus decision

The MarketExpert may report:

```text
WHEAT
price = X
inventory = Y
trend = ...
market_pressure = ...
```

It does not conclude:

```text
BUY WHEAT
```

The decision belongs to a later layer that combines market, inventory, financial, livestock, agricultural and operational information.

---

# 9.6 OpponentExpert

## Status

**Implemented**

## Responsibility

`OpponentExpert` describes only state observable in `obs["farms"][opponent]`, including public cash, farm tiles, visible crops/production and placed animals. It does not access `obs["private"]`, infer intentions or actions, compare players, or calculate complete opponent net worth. Relative and competitive interpretation belongs to a future layer.

# 10. OperationsExpert

## Status

**Planned**

## Responsibility

`OperationsExpert` will represent the player's operational capacity and execution context.

It answers:

> What can the player physically execute now?

It will describe:

### Farmer

* farmer position
* farmer x
* farmer y

### Farm hands

* number of hands
* hands hired today
* current hand availability
* operational capacity

### Tasks

* actionable tasks
* pending tasks
* estimated workload
* estimated actions required

### Distances

Potential features include:

* distance to shed
* distance to nearest plant
* distance to nearest animal
* distance to nearest weed
* distance to nearest empty tile

`distance_to_shed` remains pending confirmation of the actual shed position representation.

OperationsExpert describes capacity and execution cost.

It does not decide the optimal task.

---

# 11. ProductionExpert

## Status

**Planned**

## Responsibility

`ProductionExpert` is an **integration layer**.

It does not replace `AgricultureExpert` or `LivestockExpert`.

It answers:

> How much production does the farm currently have, and what production is currently available or approaching?

Its information comes from existing domain states.

Conceptually:

```text
AgricultureExpert
       │
       ├── crop production
       │
       ▼
ProductionExpert
       ▲
       │
       ├── livestock production
       │
LivestockExpert
```

Potential features include:

* current production
* production ready now
* production in progress
* production capacity
* remaining production
* crop production
* animal production
* integrated production

Features involving future prediction or expected economic value belong to later analytical layers unless they can be derived deterministically from verified game rules.

---

# 12. Feature Ownership

Every feature has one logical owner.

| Feature                   | Owner             |
| ------------------------- | ----------------- |
| `cash`                    | FinancialExpert   |
| `net_worth`               | FinancialExpert   |
| `liquidity_ratio`         | FinancialExpert   |
| `animal_asset_value`      | FinancialExpert   |
| `inventory_value`         | FinancialExpert   |
| `land_value`              | FinancialExpert   |
| `crop_state`              | AgricultureExpert |
| `watered_today`           | AgricultureExpert |
| `crop_yield`              | AgricultureExpert |
| `animal_state`            | LivestockExpert   |
| `animal_details`          | LivestockExpert   |
| `needs_feed`              | LivestockExpert   |
| `animal_production_state` | LivestockExpert   |
| `shed_stock`              | InventoryExpert   |
| `inventory_capacity`      | InventoryExpert   |
| `seed_stock`              | InventoryExpert   |
| `market_price`            | MarketExpert      |
| `price_trend`             | MarketExpert      |
| `market_pressure`         | MarketExpert      |
| `opponent_cash`           | OpponentExpert    |
| `opponent_visible_crops`  | OpponentExpert    |
| `opponent_placed_animals` | OpponentExpert    |
| `farmer_position`         | OperationsExpert  |
| `hands_count`             | OperationsExpert  |
| `integrated_production`   | ProductionExpert  |

An Expert may consume a feature owned by another Expert, but it does not become the owner of that feature.

---

# 13. Communication Between Experts

The standard interface is:

```python
expert.process_observation(obs)
```

This updates the Expert's internal state.

The complete public feature set is exposed through:

```python
expert.get_features()
```

Individual values are exposed through:

```python
expert.get_xxx()
```

---

# 14. Expert Encapsulation

An Expert may query another Expert:

```python
cash = financial.get_cash()
```

This is valid.

An Expert must not modify another Expert's internal state:

```python
financial.cash = 500
```

This violates the architecture.

The relationship is:

```text
Expert A
    │
    │ query
    ▼
Expert B
    │
    └── returns information
```

not:

```text
Expert A
    │
    │ modifies
    ▼
Expert B
```

---

# 15. Deterministic Business Layer

The current Business Experts are intentionally deterministic.

Their responsibility is:

```text
RAW OBSERVATION
       │
       ▼
Business Experts
       │
       ▼
Domain State
       │
       ▼
Semantic State
```

The Experts should first represent the game correctly before introducing predictive models.

This allows every domain to be independently tested against actual observations.

---

# 16. Domain State vs Cross-Domain Features

This distinction is now fundamental.

## Domain State

Each Expert describes facts belonging to its own domain.

Examples:

```text
FinancialExpert
    cash = 190

InventoryExpert
    wheat = 0

LivestockExpert
    cow = 1
    needs_feed = True

MarketExpert
    wheat_price = X
```

These are domain facts.

---

## SemanticState and cross-domain meaning

In the current architecture, `SemanticState` combines validated domain facts and contains cross-domain semantic features in its `situations`, `relationships`, `risks` and `opportunities` groups. There is no required separate synthetic-feature layer after it.

For example:

```text
Livestock:
    cow = 1
    needs_feed = True

Inventory:
    wheat = 0

Financial:
    cash = 190

Market:
    wheat available = True
```

This can generate a semantic situation such as:

```text
animal_feed_shortage = True
```

or:

```text
livestock_maintenance_risk = True
```

These are **not raw domain facts**. They are candidate cross-domain meanings belonging inside `SemanticState` after their source, rule, granularity, redundancy and leakage have been validated.

---

# 17. Features Intentionally Postponed

The following belong to later analytical layers.

## Prediction

Examples:

```text
future_price_prediction
future_market_state
future_production_prediction
```

These require historical data and/or predictive models.

---

## Optimization

Examples:

```text
optimal_crop
optimal_action
opportunity_cost
optimal livestock composition
optimal resource allocation
```

These require a decision or optimization layer.

---

## Asset Attribution

Examples:

```text
ROI of individual animal
ROI of individual crop
ROI of individual structure
ROI of individual land quadrant
individual asset payback
```

These require causal/temporal attribution.

---

## Opponent Prediction

Examples:

```text
opponent_future_strategy
opponent_future_state
```

These belong to later analytical or ML layers.

The agent must not use information unavailable to it during real inference.

---

# 18. Semantic State

The next architectural layer is a unified semantic representation of the current game state.

Conceptually:

```text
OBS
 │
 ├── FinancialExpert
 │
 ├── AgricultureExpert
 │
 ├── InventoryExpert
 │
 ├── LivestockExpert
 │
 └── MarketExpert
          │
          ▼
     Semantic State
```

A semantic state could contain:

```text
financial:
    cash
    assets
    net_worth
    liquidity

agriculture:
    crops
    ready_crops
    unwatered_crops
    agricultural_surface

inventory:
    seeds
    shed
    carried
    capacity

livestock:
    animals
    needs_feed
    production_state

market:
    prices
    inventory
    trends
    pressure
```

The Semantic State should not make decisions.

Its purpose is to provide a clean representation of the current state to later layers.

---

# 19. Long-Term Architecture (Historical Proposal)

The complete architecture is therefore:

```text
        RAW OBSERVATION
            ↓
        Six implemented Business Experts
            ↓
        Domain facts
            ↓
        SemanticState
          situations / relationships / risks / opportunities
            ↓
        Model-specific features
            ↓
        Specialized Decision Experts + Coordinator
            ↓
        ACTION
```

        Reward and credit assignment are future training/evaluation architecture, not layers currently implemented in the action path. `StrategicExpert` is also future; it will describe competitive state, not choose actions.

        The current semantic boundary is:

```text
Business Experts
    ↓
describe the state

SemanticState
    ↓
integrates domain facts and validated cross-domain meaning

Model-specific features
    ↓
prepare inputs for a decision model

Decision Experts + Coordinator
    ↓
select an action
```

---

# 20. Current Implementation Roadmap

The implementation should now proceed in phases.

## Phase 1 — Deterministic Domain Experts (Historical Status)

```text
FinancialExpert       DONE
AgricultureExpert     DONE
InventoryExpert       DONE
LivestockExpert       DONE
MarketExpert          DONE
OpponentExpert        DONE
```

These six form the currently implemented deterministic Business Expert layer.

---

## Phase 2 — Validate the Domain Layer

Before adding unnecessary complexity:

1. Feed real observations to every Expert.
2. Verify that every Expert reconstructs its domain correctly.
3. Test day transitions.
4. Test resource movements.
5. Test animal lifecycle.
6. Test crop lifecycle.
7. Test market state changes.
8. Verify that no feature is duplicated between Experts.
9. Verify that no Expert performs decisions.

The recent cow disappearance test is an example of this validation phase.

---

## Phase 3 - SemanticState (Implemented baseline; ongoing audit)

`SemanticState` combines facts from Financial, Agriculture, Inventory, Livestock, Market and observable public Opponent information into the stable categories `situations`, `relationships`, `risks` and `opportunities`. It currently emits 14 features. Consult `Semantic contract.md` for the exact names, sources and rules.

The ongoing work is to validate and improve this shared semantic feature catalog. Candidate patterns are hypotheses and enter the implementation only after their source, deterministic rule, retained context, granularity, redundancy and leakage have been reviewed.

---

## Phase 4 - Model-specific datasets (Future)

Each future model will have a task-specific target and input feature set selected or transformed from the shared `SemanticState` catalog. Define those separately before creating its training dataset. `semantic_dataset.jsonl` is an observation/action log for inspection and collection; it does not itself define every model's dataset, target, or training process.

---

## Future — OperationsExpert

Implement `OperationsExpert` only after the basic Semantic State is stable.

Operations can then contribute execution-related information:

```text
what can be executed
how much operational capacity exists
where the player is
what tasks are physically accessible
```

---

## Future — ProductionExpert

Implement `ProductionExpert` as the integration layer for:

```text
AgricultureExpert
+
LivestockExpert
```

It should aggregate production rather than duplicate domain logic.

OperationsExpert and ProductionExpert are not prerequisites for SemanticState validation or StrategicExpert. Their eventual scope and placement remain open.

## Future — StrategicExpert

The existence of `StrategicExpert` is an architectural decision, but it is not implemented. It will describe deterministic competitive state, not recommend actions or calculate reward. Whether it consumes `OpponentExpert` and other experts or reconstructs its inputs directly from `obs` remains open. It follows validated SemanticState features and precedes future state-transition/reward work.

---

## Phase 7 — State Transitions

Once the current state is reliable:

```text
state_t
   │
   │ action_t
   ▼
game
   │
   ▼
state_t+1
```

The system can calculate deterministic transitions:

```text
Δcash
Δinventory
Δproduction
Δlivestock
Δagriculture
Δmarket
```

---

## Phase 8 — Reward and Credit Assignment

Only after state transitions are reliable should we build:

```text
reward_t
```

and later:

```text
credit assignment
```

The objective is to distinguish:

```text
state value
```

from:

```text
contribution of action
```

and from:

```text
delayed consequences
```

---

## Phase 9 — ML / RL

Only after the deterministic representation is validated should Machine Learning or Reinforcement Learning be introduced.

The long-term training representation can become:

```text
state_t
action_t
state_t+1
reward_t
game_result
```

with opponent information restricted to what would actually be observable during inference.

---

# 21. Current Position and Recommended Next Step

The current pipeline is:

```text
RAW OBSERVATION
    ->
Six Business Experts (deterministic domain facts)
    ->
SemanticState (14 shared semantic features; contract in Semantic contract.md)
    ->
Future: model-specific feature selection / transformation
    ->
Future: separate datasets and targets for each model
    ->
Future: model training and evaluation
```

The immediate work remains the quality and coverage of the shared `SemanticState` feature catalog: validate sources and rules, retain useful context, preserve product-level information, and avoid redundant or action/target-leaking features. Candidate patterns are not automatically approved. Do not treat reward, credit assignment, or RL as the next step; those belong to a later, separately approved phase.

`semantic_dataset.jsonl` currently provides a chronological record of semantic observations and actions. It is useful for inspection and data collection, but it is not yet a set of model-specific training datasets and does not establish training targets by itself.
