# Kaggriculture — Reward Distribution & Credit Assignment Brainstorming

> **Status:** future architecture and hypothesis space, not current implementation. `StrategicExpert`, `StateTransition`, `RewardEngine`, `CreditAssignment`, Decision Experts and Coordinator are not implemented. Reward formulas below are candidates, not decisions. Current project position: `SemanticState` already contains 14 shared semantic features (8 situations, 3 relationships, 3 risks; see `Semantic contract.md`). Improving that feature catalog and later constructing distinct model-specific datasets precede this document’s reward/credit-assignment work. No model training or reward implementation is implied by the semantic log.

## 1. Objective

The objective of this document is to define how rewards should be distributed across the sequence of decisions made by an agent in Kaggriculture.

The central problem is:

> **What makes an action good or bad when the final result of the game alone is not sufficient to evaluate it?**

The goal is not initially to define the final reinforcement-learning algorithm.

The goal is to establish a rational, deterministic and explainable **reward signal** that can later be used for:

* supervised learning
* reinforcement learning
* action evaluation
* policy learning
* decision analysis
* historical game analysis

The fundamental hypothesis is:

> **The quality of an action should be evaluated according to its contribution to the evolution of the farm's economic, productive, operational and competitive state, not only according to the final result of the game.**

A second important hypothesis is:

> **The absolute value of an economic result is not sufficient to determine whether an action was good. Its value must be interpreted in the context of the player's trajectory and, where possible, relative to the observable state of the opponent.**

A third hypothesis has now emerged:

> **Competitive strategy is sufficiently important to justify a dedicated Business Expert responsible for representing the player's strategic position relative to the observable opponent.**

This Strategic / Competitive Expert does not make the final decision and does not calculate the reward. It provides the semantic state required to evaluate competitive consequences.

---

# 2. The problem with using the final result as the target

A first intuitive approach would be to use the final amount of money or final liquidity as the target.

For example:

```text
Game A → final money = 100,000
Game B → final money = 90,000
```

It would appear that:

```text
100,000 > 90,000
```

therefore Game A was better.

However:

```text
Game C → final money = 10,000
Game D → final money = 5,000
```

The absolute values cannot be compared directly with the first games.

A farm ending with:

```text
10,000
```

may have performed much better than another farm ending with:

```text
90,000
```

if initial conditions, investments, assets, production and economic trajectory were different.

Therefore:

> **Absolute final liquidity is not a sufficiently robust target.**

The same principle applies to:

* cash
* net worth
* inventory value
* production
* number of animals
* accumulated income
* any other isolated absolute quantity

---

# 3. The football analogy: absolute performance is not victory

An important conceptual insight is provided by competitive sports.

Suppose:

```text
Match A

Team A scores 3
Team B scores 4

→ LOSS
```

and:

```text
Match B

Team A scores 2
Team B scores 0

→ WIN
```

The team scored:

```text
3 goals in a loss
2 goals in a win
```

Therefore:

```text
3 goals ≠ necessarily better than 2 goals
```

The number of goals alone does not determine whether the performance was successful.

The relevant quantity is the **competitive result**.

The same conceptual problem exists in Kaggriculture.

For example:

```text
Player:
+20% net worth

Opponent:
+30% net worth
```

versus:

```text
Player:
+10% net worth

Opponent:
+2% net worth
```

A positive economic change is not automatically a positive competitive change.

Therefore the reward system should distinguish:

```text
OWN PROGRESS
```

from:

```text
COMPETITIVE PROGRESS
```

---

# 4. Kaggriculture is a sequential competitive decision problem

A Kaggriculture game is not a collection of independent observations.

It is a sequence:

```text
Observation₀
    ↓
Action₀
    ↓
Observation₁
    ↓
Action₁
    ↓
Observation₂
    ↓
...
    ↓
Observation₇₁₉
```

Each action changes the state of the farm.

At the same time, the opponent is changing its own state.

Therefore the problem is closer to:

```text
Own state
    +
Opponent observable state
    +
Strategic context
    +
Action
    ↓
New own state
    +
New opponent observable state
    ↓
Economic / productive / competitive consequence
```

This introduces an explicit strategic dimension.

---

# 5. Business Experts and their responsibilities

The current implementation contains six Business Experts:

```text
FinancialExpert
    ↓
Economic / financial state

AgricultureExpert
    ↓
Agricultural state

LivestockExpert
    ↓
Livestock state

InventoryExpert
    ↓
Physical inventory state

MarketExpert
    ↓
Market and price state

OpponentExpert
    ↓
Observable opponent state only
```

`OperationsExpert`, `ProductionExpert` and `StrategicExpert` are future components, not members of the implemented six.

| Component | Status |
| --- | --- |
| FinancialExpert | Implemented |
| AgricultureExpert | Implemented |
| InventoryExpert | Implemented |
| LivestockExpert | Implemented |
| MarketExpert | Implemented |
| OpponentExpert | Implemented; observable opponent facts only |
| OperationsExpert | Not implemented; future |
| ProductionExpert | Not implemented; future role/interface to validate |
| StrategicExpert | Existence decided; not implemented; sources/interface open |

`OpponentExpert` owns observable opponent facts. `StrategicExpert`, when implemented, may interpret those facts relative to our own state; it must not be conflated with the opponent facts expert or treated as a decision maker.

The experts answer:

> **What is happening in each business domain?**

They do not necessarily decide what the agent should do.

The distinction is fundamental.

---

# 6. Strategic / Competitive Expert

A dedicated **StrategicExpert** should be considered part of the Business Expert layer.

Its responsibility is to represent the player's current **strategic and competitive position**.

It should answer questions such as:

```text
Where am I relative to the opponent?

Is my economic position improving or deteriorating?

Is my productive capacity increasing relative to the opponent?

Am I expanding faster or slower?

Am I accumulating a strategic advantage or disadvantage?

How much time remains?

Is the current position aggressive, defensive, balanced or transitional?

Which observable competitive dimensions are changing?
```

The expert should initially remain deterministic.

It should not make strategic decisions.

It should not calculate the final reward.

It should not contain ML.

---

# 7. StrategicExpert is not a "decision maker"

The StrategicExpert should NOT directly answer:

```text
BUY COW
```

or:

```text
SELL WHEAT
```

or:

```text
EXPAND LAND
```

Those are decisions belonging to a higher-level decision/policy layer.

The StrategicExpert should instead provide information such as:

```text
relative_net_worth
relative_cash
relative_land
relative_production_capacity
relative_animal_capacity
economic_growth_difference
production_growth_difference
remaining_time
competitive_position
```

The decision layer can then use these features.

Therefore:

```text
StrategicExpert
    ↓
describes strategic position

Decision / Policy
    ↓
chooses action
```

---

# 8. Strategic state versus strategic decision

This distinction should be explicit.

### Strategic state

Describes:

```text
what the competitive situation currently is
```

### Strategic decision

Answers:

```text
what should I do because of that situation?
```

For example:

```text
Strategic state:

own net worth growth = +8%
opponent net worth growth = +12%
own production capacity = increasing
opponent production capacity = increasing faster
remaining days = 5
```

The StrategicExpert reports this state.

It should not automatically conclude:

```text
BUY ANIMAL
```

or:

```text
SELL EVERYTHING
```

That decision belongs elsewhere.

---

# 9. StrategicExpert inputs

The StrategicExpert should consume semantic information from the game observation and, where appropriate, from the other Business Experts.

Conceptually:

```text
OBS
 │
 ├── Financial state
 ├── Agriculture state
 ├── Livestock state
 ├── Inventory state
 ├── Market state
 └── Operations state
          │
          ▼
    StrategicExpert
          │
          ▼
   Strategic state
```

The following architectural question remains open:

> Should StrategicExpert directly depend on other Experts, or independently reconstruct the required information from `obs`?

Whether it reconstructs directly from `obs` or consumes `OpponentExpert` and other Expert outputs is not decided. Preserve this as an open interface decision; do not encode either approach as settled architecture.

Later, a higher-level orchestration layer can combine their outputs.

---

# 10. Public opponent information

`OpponentExpert` currently extracts observable cash, farmer position, tile counts, visible crops/production and placed-animal details from `obs["farms"][opponent]`. It does not read `obs["private"]`, expose the opponent's private inventory or calculate complete opponent net worth. `StrategicExpert` may later interpret these facts relative to our own state.

Only information genuinely observable during gameplay may become an inference feature. Verify each field against the runtime observation schema before use. Other candidate public fields include, subject to verification:

```text
opponent.money
opponent.tiles
opponent.farmer_position
opponent.hands
opponent.unlocked_land
opponent.visible structures
opponent.visible plants
opponent.visible animals
```

These raw variables should be transformed into meaningful semantic features.

For example:

```text
opponent_cash

opponent_unlocked_land

opponent_cultivated_surface

opponent_crop_count

opponent_animal_structures

opponent_visible_production

opponent_operational_capacity
```

---

# 11. Private opponent information and leakage

Historical replay files may expose information that would not be available during real gameplay.

For example:

```text
opponent.private.shed
opponent.private.seeds
opponent.private.inventories
```

If these are not available to the agent during inference, they must not become model input.

Otherwise:

```text
TRAINING INFORMATION
        ≠
INFERENCE INFORMATION
```

and the model would suffer from information leakage / train-inference mismatch.

The StrategicExpert therefore needs two conceptual information boundaries:

```text
PUBLIC STRATEGIC STATE
```

for inference and model input,

and:

```text
RETROSPECTIVE STRATEGIC INFORMATION
```

which may be used during historical analysis and reward reconstruction.

---

# 12. Candidate Strategic Features

The StrategicExpert may eventually produce features such as:

### Economic position

```text
own_net_worth
opponent_public_net_worth
relative_net_worth
```

### Economic growth

```text
own_net_worth_delta
opponent_net_worth_delta
relative_net_worth_delta
```

### Liquidity

```text
own_cash
opponent_cash
relative_cash
```

### Expansion

```text
own_unlocked_land
opponent_unlocked_land
relative_land
```

### Production

```text
own_production_capacity
opponent_production_capacity
relative_production_capacity
```

### Agriculture

```text
own_cultivated_surface
opponent_cultivated_surface
relative_cultivated_surface
```

### Livestock

```text
own_visible_animal_capacity
opponent_visible_animal_capacity
relative_animal_capacity
```

### Time

```text
day
hour
days_remaining
steps_remaining
```

The final list must be validated against the actual observation schema.

---

# 13. Relative competitive state

A conceptual variable could be:

```text
relative_net_worth =
    own_net_worth - opponent_net_worth
```

and its transition:

```text
Δrelative_net_worth =
    relative_net_worth_after
    -
    relative_net_worth_before
```

Equivalent concepts can be considered for:

```text
cash
land
production capacity
cultivated surface
visible livestock capacity
other strategically meaningful public variables
```

However:

> **Not every difference between players is necessarily strategically meaningful.**

Feature selection must therefore be validated experimentally.

---

# 14. Strategic trajectory

The StrategicExpert should eventually distinguish the current state from the trajectory.

For example:

```text
Current relative position:
-5%
```

does not tell us whether the player is:

```text
recovering
```

or:

```text
falling further behind
```

Therefore temporal features may be required:

```text
relative_position_t
relative_position_t-1
relative_position_t-k
```

and:

```text
competitive_trend
```

This is important because strategy concerns not only:

```text
where am I?
```

but also:

```text
where am I going?
```

---

# 15. Strategic context and remaining time

The same competitive position can have different meanings depending on the remaining time.

For example:

```text
Player behind
```

at:

```text
day 5
```

is not necessarily equivalent to:

```text
Player behind
```

at:

```text
day 29
```

Therefore strategic state must incorporate temporal context:

```text
competitive_position
+
remaining_time
+
trajectory
```

This allows the learning system to distinguish between:

```text
recoverable disadvantage
```

and:

```text
late-game disadvantage
```

without requiring the StrategicExpert itself to make a decision.

---

# 16. StrategicExpert and the Reward Engine

The StrategicExpert does not calculate the reward.

Instead:

```text
OBS
 │
 ├── FinancialExpert
 ├── AgricultureExpert
 ├── LivestockExpert
 ├── InventoryExpert
 ├── MarketExpert
 ├── OperationsExpert
 └── StrategicExpert
          │
          ▼
    Semantic State
          │
          ▼
     Reward Engine
```

The Reward Engine then evaluates the transition.

For example:

```text
Strategic state_t
        ↓
Action
        ↓
Strategic state_t+1
        ↓
Competitive progress
```

This becomes one component of the overall reward.

---

# 17. Own progress versus competitive progress

The reward architecture should explicitly maintain two different concepts:

```text
OWN PROGRESS
```

and:

```text
COMPETITIVE PROGRESS
```

Own progress may contain:

```text
Δliquidity
Δnet_worth
Δassets
Δproduction
Δproductive_capacity
```

Competitive progress may contain:

```text
Δrelative_net_worth
Δrelative_production
Δrelative_land
Δrelative_capacity
```

They should initially remain separate.

Only afterward should the Reward Engine investigate how they should be combined.

---

# 18. Strategic progress is not identical to winning

The StrategicExpert should not produce:

```text
WIN
LOSS
```

as its primary output.

Instead it should describe:

```text
competitive state
competitive trajectory
relative progress
```

The final game result remains a terminal/contextual variable.

This prevents:

```text
WIN = every previous strategic state was good
```

and:

```text
LOSS = every previous strategic state was bad
```

---

# 19. Economic quality versus competitive quality

The introduction of StrategicExpert reinforces an important distinction.

An action can be:

```text
economically positive
```

while:

```text
competitively insufficient
```

For example:

```text
SELL WHEAT

Own:
+8% liquidity
+5% net worth

Opponent:
+12% comparable economic progress
```

The action may still have created economic value.

The strategic consequence is simply different.

Therefore the Reward Engine should preserve:

```text
economic_score
```

and:

```text
competitive_score
```

as separate dimensions before combining them.

---

# 20. Strategic decisions and opportunity cost

The StrategicExpert may also eventually help represent **opportunity cost**, but this must be treated carefully.

For example:

```text
Player has 1000 cash.

Option A:
BUY COW

Option B:
BUY LAND

Option C:
BUY SEEDS
```

The StrategicExpert should not decide which option is best.

However, the state representation may expose:

```text
remaining liquidity
available productive capacity
relative competitive position
remaining time
opponent expansion
```

which allows a later decision model to learn that the same investment may have different strategic implications in different contexts.

Thus:

```text
StrategicExpert
    ↓
context

Decision model
    ↓
choice
```

---

# 21. Business Experts as semantic state generators

The Business Experts therefore form a semantic representation layer:

```text
OBSERVATION
     │
     ├── FinancialExpert
     │
     ├── AgricultureExpert
     │
     ├── LivestockExpert
     │
     ├── InventoryExpert
     │
     ├── MarketExpert
     │
     ├── OperationsExpert
     │
     └── StrategicExpert
     │
     ▼
SEMANTIC STATE
```

Each expert has a bounded responsibility.

The StrategicExpert does not replace:

```text
FinancialExpert
AgricultureExpert
LivestockExpert
InventoryExpert
MarketExpert
OperationsExpert
```

It interprets their relevant competitive context at a separate semantic level.

---

# 22. Reward Engine

The Reward Engine answers:

> **How did the state transition affect the farm economically, productively, operationally and competitively?**

Conceptually:

```text
state_t
   +
action_t
   +
state_t+1
   ↓
Reward Engine
```

It may calculate:

```text
own_economic_progress

production_progress

operational_progress

competitive_progress

delayed_consequences
```

The exact formula remains undefined.

---

# 23. Credit Assignment Layer

The Credit Assignment Layer answers a different question:

> **Which previous actions deserve credit or blame for the observed consequence?**

This distinction is important:

```text
Reward Engine
    ↓
How good was the state transition?

Credit Assignment
    ↓
Which previous actions contributed to that result?
```

The StrategicExpert belongs before these layers.

It does not perform either task.

---

# 24. Causal chains

Examples include:

```text
BUY SEED
    ↓
PLANT
    ↓
WATER
    ↓
GROW
    ↓
HARVEST
    ↓
SELL
```

and:

```text
BUY ANIMAL
    ↓
PICKUP
    ↓
PLACE
    ↓
CARE
    ↓
PRODUCE
    ↓
SELL
```

Competitive context can affect the interpretation of the chain.

For example:

```text
BUY COW
```

may have different strategic consequences depending on:

```text
remaining time
own production
opponent production
own liquidity
opponent expansion
```

The action itself has not changed.

The context has.

---

# 25. Delayed consequences

Kaggriculture contains actions whose effects appear later.

Example:

```text
BUY SEED
    ↓
PLANT
    ↓
WATER
    ↓
GROW
    ↓
HARVEST
    ↓
SELL
```

The financial benefit appears at the end.

Therefore assigning the complete reward only to:

```text
SELL
```

would reproduce the credit-assignment problem.

The reward must be capable of assigning credit to earlier relevant actions.

The StrategicExpert can provide the competitive context in which those delayed consequences occurred.

---

# 26. Immediate versus delayed reward

Two concepts should remain distinct.

### Immediate reward

Measures the direct state transition.

Example:

```text
BUY COW

cash ↓
animal assets ↑
net worth ≈
```

### Delayed reward

Measures future consequences.

Example:

```text
BUY COW
    ↓
CARE
    ↓
PRODUCTION
    ↓
SELL
```

Therefore:

```text
immediate component
+
delayed component
```

may eventually be required.

---

# 27. Final result

The final result remains important:

```text
WIN
DRAW
LOSS
```

but should not automatically label every action.

A losing player can have:

```text
good actions
bad actions
good investments
poor timing
```

A winning player can also have:

```text
good actions
bad actions
avoidable losses
```

Therefore historical games should preserve action-level information.

---

# 28. Historical analysis versus model input

This distinction remains mandatory.

Historical replay:

```text
may contain complete information
```

Historical reward reconstruction:

```text
may use retrospective information
to understand what happened
```

Model input:

```text
must contain only information
available during actual inference
```

Therefore:

```text
historical information
        ≠
model input
```

The StrategicExpert must respect this same restriction.

---

# 29. Candidate reward architecture

The conceptual reward may eventually contain:

```text
reward =
    own_economic_score
    +
    production_score
    +
    operational_score
    +
    competitive_score
    +
    delayed_consequence_score
```

The competitive component could be:

```text
competitive_score =
    f(
        Δrelative_economic_position,
        Δrelative_production_position,
        Δrelative_expansion,
        ...
    )
```

No final formula has been selected.

The important architectural decision is that:

```text
competitive information
```

has a dedicated semantic source:

```text
StrategicExpert
```

---

# 30. Reward must remain deterministic initially

Given:

```text
state_t
action_t
state_t+1
```

the reward calculation should initially be deterministic.

The same transition should produce the same reward.

Therefore:

```text
reward_engine(
    state_t,
    action_t,
    state_t+1
)
```

should be reproducible.

The StrategicExpert should also initially be deterministic.

Machine learning should learn from the resulting signal, not determine the reward itself.

---

# 31. Candidate Long-Term Architecture

The following is a future architecture, not a description of implemented code:

```text
RAW OBSERVATION
    ↓
Six implemented Business Experts
    ↓
Domain facts
    ↓
SemanticState (14 shared semantic features; see Semantic contract.md)
    ↓
StrategicExpert → competitive / strategic state (future; interface open)
    ↓
StateTransition → RewardEngine → CreditAssignment (future)
    ↓
Model-specific features
    ↓
Specialized Decision Experts
    ↓
Decision Coordinator
    ↓
ACTION
```

---

# 32. Important architectural distinction

The architecture now contains four conceptually different layers.

## Business Experts

Answer:

> **What happened?**

Current implemented examples:

```text
FinancialExpert
AgricultureExpert
LivestockExpert
InventoryExpert
MarketExpert
OpponentExpert
```

`OperationsExpert` and `StrategicExpert` remain future components; `ProductionExpert` is also unimplemented and its eventual boundary remains to be validated.

## Reward Engine

Answers:

> **What was the consequence of the transition?**

## Credit Assignment

Answers:

> **Which previous actions contributed to that consequence?**

## Learning / Decision Model

Answers:

> **Given the current state, which action should be selected?**

The future decision layer is specialized and coordinated:

```text
SemanticState
    ↓
Strategic / Competitive State
    ↓
StateTransition → RewardEngine → CreditAssignment
    ↓
Decision Experts → Coordinator → Action
```

---

# 33. What the StrategicExpert adds

The StrategicExpert introduces something that the previous architecture did not represent explicitly.

Without it:

```text
Financial state
Production state
Operations state
```

could be evaluated independently.

With it:

```text
Own state
    +
Opponent public state
    +
Time
    +
Trajectory
    ↓
Strategic state
```

This makes it possible to distinguish:

```text
"my farm is improving"
```

from:

```text
"my farm is improving faster than the opponent"
```

and:

```text
"my farm is economically healthy"
```

from:

```text
"my farm is economically healthy but strategically falling behind"
```

These are different pieces of information.

---

# 34. What the StrategicExpert must NOT do

The StrategicExpert should not become a "god expert".

It should NOT:

* manage money
* calculate accounting
* manage inventory
* manage crop state
* manage animal state
* manage market prices
* execute actions
* calculate the final reward
* assign credit
* train ML models
* decide the final action

Its responsibility is specifically:

> **Represent the current competitive and strategic context using information available to the agent.**

---

# 35. Current open question: how much strategy belongs here?

The existence of a StrategicExpert does not mean that every strategic concept belongs inside it.

A useful boundary is:

```text
STATE
```

versus:

```text
DECISION
```

The StrategicExpert should primarily represent:

```text
strategic state
```

rather than:

```text
strategic policy
```

For example:

```text
relative production = -12%
```

belongs to StrategicExpert.

But:

```text
therefore BUY COW
```

belongs to the decision layer.

This boundary should be preserved.

---

# 36. Updated central hypothesis

The central hypothesis has therefore evolved again.

It is no longer simply:

> **"How much did this action improve the farm?"**

nor:

> **"How much did the farm improve relative to the opponent?"**

It is closer to:

> **"How much did this decision contribute to improving the farm's economic, productive and operational trajectory, and how did it affect the player's strategic position relative to the publicly observable state and trajectory of the opponent?"**

This requires both:

```text
Business state
```

and:

```text
Strategic state
```

---

# 37. Updated long-term architecture

The long-term architecture is now:

```text
                         GAME HISTORY
                              │
                              ▼
                       RAW OBSERVATIONS
                              │
                              ▼
                       Business Experts
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
       Own state       Opponent public state   Time/context
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       StrategicExpert
                              │
                              ▼
                       Semantic State
                              │
                              ▼
                       State Transition
                              │
                              ▼
                        Reward Engine
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
           Own progress          Competitive progress
                 │                         │
                 └────────────┬────────────┘
                              ▼
                        Reward Signal
                              │
                              ▼
                       Credit Assignment
                              │
                              ▼
                       Training Dataset
                              │
                              ▼
                           ML / RL
                              │
                              ▼
                           ACTION
```

The critical restriction remains:

```text
MODEL INPUT
    ↓
ONLY INFORMATION AVAILABLE AT INFERENCE
```

while:

```text
HISTORICAL ANALYSIS
    ↓
may inspect additional retrospective information
```

---

# 38. Updated development phase

This is a future reward/credit-assignment roadmap. It starts only after the shared semantic catalog and any task-specific datasets needed for a model are defined; it is not the current implementation checklist. Before implementing the final reward function:

### Step 1 - Maintain the shared SemanticState catalog

The current implementation has 14 shared semantic features. Keep their definitions aligned with the code and `Semantic contract.md`; review new candidates before implementation.

### Step 2 - Define model-specific datasets (future, before training)

For each model, specify its task and target, observation-time inputs, sampling unit and evaluation approach. Select or transform the relevant features from the shared catalog. `semantic_dataset.jsonl` is a log of semantic observations and actions, not a finalized model-specific training dataset.

### Step 3 — Define public opponent information

Verify exactly which opponent variables are observable during real gameplay.

### Step 4 — Decide StrategicExpert sources/interface, then implement

Initially deterministic and descriptive.

It should produce:

```text
current competitive state
relative state
trajectory features
time context
```

### Step 5 — Define state deltas

Compare:

```text
state_t
```

with:

```text
state_t+1
```

### Step 6 — Define own economic transitions

For example:

```text
liquidity ↓ / net_worth ≈
liquidity ↓ / net_worth ↑
liquidity ↓ / net_worth ↓
liquidity ↑ / net_worth ↑
...
```

### Step 7 — Define competitive transitions

For example:

```text
relative position ↑
relative position ≈
relative position ↓
```

together with:

```text
economic
production
expansion
```

where meaningful.

### Step 8 — Identify causal action chains

Examples:

```text
seed → planting → care → harvest → sale
```

```text
animal → placement → care → production → sale
```

### Step 9 — Define reward attribution

Determine how consequences should be distributed among contributing actions.

### Step 10 — Define temporal horizons

Different action classes may require different horizons.

### Step 11 — Normalize the reward

Determine an appropriate scale.

### Step 12 — Reconstruct historical rewards

Apply the deterministic system to real trajectories.

Inspect:

```text
reward by action
reward by action chain
reward by game
reward by winner/loser
own-progress reward
competitive-progress reward
```

### Step 13 — Validate information availability

Ensure that every model feature was actually available at inference time.

### Step 14 — Validate strategic reasoning

Inspect cases such as:

```text
economically positive + competitively positive

economically positive + competitively insufficient

economically neutral + strategically valuable

economically negative + strategically justified investment

economically negative + strategically negative action
```

### Step 15 — Validate against human reasoning

Inspect obvious cases:

```text
good investment
bad investment
productive action
wasted action
successful production chain
failed production chain
good action inside a losing game
bad action inside a winning game
```

### Step 16 — Compare reward with final result

Measure whether action-level rewards provide useful information without simply reproducing:

```text
WIN = good
LOSS = bad
```

### Step 17 — Define the decision architecture, then select learning strategy

Consider:

```text
supervised learning
reinforcement learning
hybrid learning
```

Decision outputs such as `BUY_COW` belong to Decision Expert targets, never to `SemanticState`. The intended future path uses multiple specialized Decision Experts and a final Coordinator; neither is implemented today.

---

# 39. Final conceptual objective

The long-term objective is not to create a model that merely memorizes:

```text
"winning games look like this"
```

The objective is to create a model capable of learning:

```text
"given this state,
this action tends to improve my future position."
```

and eventually:

```text
"given this state and the observable state and trajectory
of the opponent, this action tends to improve my future
position and my ability to achieve the competitive objective."
```

The desired learning process is therefore:

```text
OBSERVATION
    ↓
BUSINESS UNDERSTANDING
    ↓
STRATEGIC UNDERSTANDING
    ↓
ACTION
    ↓
CONSEQUENCE
    ↓
OWN PROGRESS
    +
COMPETITIVE PROGRESS
    ↓
REWARD
    ↓
CREDIT ASSIGNMENT
    ↓
LEARNING
    ↓
BETTER ACTION
```

The central research question is now:

> **Can a deterministic, explainable reward and credit-assignment mechanism transform historical Kaggriculture trajectories into a meaningful action-quality signal that captures economic progress, delayed consequences and competitive position, while using only information that will actually be available at inference time?**

And an architectural question precedes it:

> **Can a dedicated StrategicExpert provide a deterministic and useful representation of competitive state without turning the Business Expert layer into a decision-making system?**

That should be tested experimentally before introducing ML/RL into the strategic layer.
