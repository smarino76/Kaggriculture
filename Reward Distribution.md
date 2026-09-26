# Kaggriculture — Reward Distribution & Credit Assignment Brainstorming

## 1. Objective

The objective of this document is to define how rewards should be distributed across the sequence of decisions made by an agent in Kaggriculture.

The central problem is:

> **What makes an action good or bad when the final result of the game alone is not sufficient to evaluate it?**

The goal is not initially to define the final reinforcement-learning algorithm.

The goal is to establish a rational and explainable **reward signal** that can later be used for:

* supervised learning
* reinforcement learning
* action evaluation
* policy learning
* decision analysis
* historical game analysis

The fundamental hypothesis is:

> **The quality of an action should be evaluated according to its contribution to the evolution of the farm's economic and operational state, not only according to the final result of the game.**

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

However, consider another game:

```text
Game C → final money = 10,000
Game D → final money = 5,000
```

The absolute values cannot be compared directly with the first games.

The same problem exists with liquidity.

A farm ending with:

```text
10,000
```

may have performed much better than another farm ending with:

```text
90,000
```

if the initial conditions, investments, assets and economic trajectory were different.

Therefore:

> **Absolute final liquidity is not a sufficiently robust target.**

---

# 3. Why final victory is also insufficient

Another possible target would be:

```text
WIN  → +1
DRAW →  0
LOSS → -1
```

This is useful for evaluating the final result, but it has an important limitation.

The final result does not tell us which individual decisions contributed to it.

Consider a sequence:

```text
t1 → action
t2 → action
t3 → action
...
t718 → action
t719 → action
```

Suppose the agent wins.

If the entire reward is assigned to the final action:

```text
t719 → +1
```

the model may incorrectly learn:

> "The last action is what causes victory."

This is a classic **credit assignment problem**.

The same problem occurs in the opposite direction:

```text
LOSS → -1
```

If the complete negative reward is assigned to the final action, the model may learn that the last action was responsible for the defeat even if the decisive mistake occurred several turns earlier.

---

# 4. Lesson from the Tic-Tac-Toe experiment

A useful conceptual reference is the previous Tic-Tac-Toe experiment.

An initial reward strategy concentrated too much reward on the final move.

The model learned an incorrect association:

```text
winning → final move
```

After analyzing the game more carefully, the reward distribution was changed.

The important insight was that the decisive contribution was often made before the final move.

For example:

```text
victory
   ↑
penultimate move → highly relevant
last move        → consequence / completion
```

Similarly, in a defeat:

```text
defeat
   ↑
earlier mistake → important negative contribution
final move      → often only the consequence
```

The improved reward distribution produced a much stronger player.

This suggests a general principle:

> **The reward should be distributed according to causal contribution, not simply according to temporal position.**

This principle is particularly relevant to Kaggriculture.

---

# 5. Kaggriculture is a sequential decision problem

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

An action may therefore have:

* immediate consequences
* delayed consequences
* indirect consequences
* economic consequences
* production consequences
* opportunity consequences

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

The economic benefit may appear much later than the original decision.

Therefore the reward mechanism must be capable of assigning credit to earlier actions.

---

# 6. The important distinction: state value vs action contribution

A critical distinction is required.

The following are not the same:

```text
state value
```

and:

```text
action contribution
```

For example, after selling wheat:

```text
cash ↑
liquidity ↑
net worth ↑
```

The observation after the sale has a better financial state.

However, the objective is not simply to say:

```text
new liquidity = target
```

Instead, we want to understand:

> **How much did the previous action contribute to the improvement?**

Therefore the learning target should preferably represent a **change or contribution**, rather than an absolute financial quantity.

---

# 7. Use normalized changes instead of absolute values

A possible starting point is to compare the state before and after an action.

For example:

```text
liquidity_before
liquidity_after
```

Instead of using:

```text
liquidity_after
```

we calculate a relative change:

```text
Δliquidity =
    (liquidity_after - liquidity_before)
    / liquidity_before
```

Similarly:

```text
Δnet_worth =
    (net_worth_after - net_worth_before)
    / net_worth_before
```

This makes observations from different games more comparable.

Example:

```text
Game A

liquidity:
100 → 108

Δ = +8%
```

and:

```text
Game B

liquidity:
1,000 → 1,080

Δ = +8%
```

The absolute values are different, but the relative change is the same.

This is much closer to what we want to measure.

---

# 8. Liquidity alone is not sufficient

Liquidity is useful, but it must not be treated as the complete reward.

Consider:

```text
BUY COW
```

The immediate effect may be:

```text
cash              ↓
liquidity         ↓
animal assets     ↑
net worth         ≈
```

If we use liquidity alone:

```text
reward < 0
```

we would incorrectly classify the investment as bad.

The action converted cash into an asset.

Therefore the reward mechanism must consider multiple dimensions.

---

# 9. Financial state decomposition

The Business Experts provide the information necessary to distinguish different types of state changes.

Important variables include:

```text
cash
liquidity
inventory_value
seed_value
animal_asset_value
land_value
assets
net_worth
cash_flow
```

This allows us to distinguish several situations.

---

# 10. Basic economic transition matrix

Consider an action that changes liquidity and net worth.

### Case A — Liquidity decreases, net worth remains approximately constant

```text
liquidity ↓
net_worth ≈ constant
```

Possible interpretation:

```text
investment
```

Example:

```text
BUY COW
```

Cash becomes an animal asset.

This should not automatically receive a negative reward.

---

### Case B — Liquidity decreases, net worth increases

```text
liquidity ↓
net_worth ↑
```

Possible interpretation:

```text
productive investment
```

This can be strongly positive.

Example:

```text
BUY SEED
→ PLANT
→ future production increases
```

or:

```text
BUY ANIMAL
→ productive asset increases
```

The exact reward should depend on context and subsequent performance.

---

### Case C — Liquidity decreases, net worth decreases

```text
liquidity ↓
net_worth ↓
```

Possible interpretation:

```text
economic loss
```

This is a strong candidate for a negative reward.

---

### Case D — Liquidity increases, net worth increases

```text
liquidity ↑
net_worth ↑
```

Possible interpretation:

```text
productive income / value creation
```

Example:

```text
SELL HARVEST
```

This is generally positive.

---

### Case E — Liquidity increases, net worth remains approximately constant

```text
liquidity ↑
net_worth ≈ constant
```

Possible interpretation:

```text
asset conversion
```

Example:

```text
SELL INVENTORY
```

The farm converts an asset into cash.

This should not necessarily receive the same reward as genuine value creation.

---

### Case F — Liquidity increases, net worth decreases

```text
liquidity ↑
net_worth ↓
```

Possible interpretation:

```text
asset liquidation / economic loss
```

The farm gained cash but lost total value.

This should potentially receive a negative or limited reward.

---

# 11. The reward should represent economic progress

The previous matrix suggests that the reward should not simply answer:

> "Did cash increase?"

Instead it should answer:

> **"Did the action improve the economic position of the farm, considering both liquidity and total value?"**

This leads to the concept of a synthetic reward score.

For example:

```text
reward_score =
    f(
        Δcash,
        Δliquidity,
        Δassets,
        Δnet_worth,
        production_change,
        inventory_change,
        operational_state
    )
```

The exact function remains to be determined.

---

# 12. Reward as a synthetic score

The target therefore does not necessarily need to be a raw game variable.

Instead:

```text
RAW OBSERVATION
       ↓
Business Experts
       ↓
Economic / operational state
       ↓
State transition
       ↓
Reward calculation
       ↓
Synthetic reward score
```

Example:

```text
t0
cash = 1,000
net_worth = 2,000

       ↓ action

BUY COW

       ↓

t1
cash = 600
animal_value = 400
net_worth = 2,000
```

The raw liquidity decreased.

But:

```text
net_worth ≈ unchanged
```

Therefore:

```text
reward ≠ strongly negative
```

The action should instead be interpreted as a capital allocation decision.

---

# 13. Delayed rewards

Kaggriculture contains actions whose effects appear later.

Example:

```text
BUY SEED
    ↓
PLANT
    ↓
WATER
    ↓
WAIT
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

would reproduce the same credit-assignment problem observed in Tic-Tac-Toe.

The reward must be capable of propagating backward through the relevant sequence.

Conceptually:

```text
SELL
 ↑
HARVEST
 ↑
GROW
 ↑
WATER
 ↑
PLANT
 ↑
BUY SEED
```

The contribution of each action should be determined according to its relevance to the resulting improvement.

---

# 14. Example: wheat production

Suppose the following sequence occurs:

```text
t1 → BUY WHEAT SEED
t2 → PLANT WHEAT
t3 → WATER
t4 → WATER
t5 → WATER
...
t10 → HARVEST
t11 → SELL WHEAT
```

At `t11`:

```text
liquidity +8%
net_worth +5%
```

A naive reward system could assign:

```text
t11 = +8%
```

and:

```text
t1...t10 = 0
```

This would be incorrect.

A better approach is to identify the relevant causal chain:

```text
BUY
 ↓
PLANT
 ↓
CARE
 ↓
HARVEST
 ↓
SELL
```

and distribute the resulting reward across the actions that enabled the production.

---

# 15. Reward attribution

The concept of **reward attribution** becomes central.

If an action at time `t` produces an effect at time `t+k`, the system should be able to associate part of the future benefit with the earlier action.

Conceptually:

```text
Future economic improvement
            │
            ▼
     attribution layer
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
     t1    t2    t3
```

The attribution mechanism must eventually answer:

> **Which previous actions were necessary or useful for producing this result?**

This is a different problem from simply measuring the state.

---

# 16. Temporal reward distribution

A possible approach is to distribute reward backward through time.

For example:

```text
Final economic improvement = +8%
```

could produce:

```text
SELL       → +2.0%
HARVEST    → +1.5%
CARE       → +1.0%
PLANT      → +2.0%
BUY SEED   → +1.5%
```

The numbers above are only illustrative.

The actual distribution must be based on a rational attribution mechanism.

Possible factors include:

* temporal distance
* causal dependency
* necessity of the action
* production contribution
* resource commitment
* financial impact
* opportunity cost
* operational state

---

# 17. Avoid arbitrary reward assignment

An important principle is:

> **Reward distribution must not be based on arbitrary intuition alone.**

For example, assigning:

```text
50% → last action
30% → previous action
20% → earlier action
```

would introduce an arbitrary bias unless there is a reason for those weights.

The system should preferably derive reward from measurable changes in the game state.

The Business Experts provide the necessary semantic information.

---

# 18. Business Experts as the reward attribution foundation

The Business Experts are therefore not only useful for feature engineering.

They may also provide the semantic information required to construct rewards.

Example:

```text
OBS
 │
 ├── FinancialExpert
 │      ├── cash
 │      ├── net_worth
 │      ├── liquidity
 │      └── asset changes
 │
 ├── AgricultureExpert
 │      ├── crop state
 │      ├── growth
 │      └── production
 │
 ├── LivestockExpert
 │      ├── animal state
 │      ├── care
 │      └── production
 │
 ├── InventoryExpert
 │      ├── stock
 │      └── inventory changes
 │
 └── OperationsExpert
        ├── actions
        └── operational cost
```

These semantic states can then be used by a dedicated:

```text
Reward / Credit Assignment Layer
```

---

# 19. Proposed separation of responsibilities

The architecture should therefore distinguish three different concepts.

## Business Experts

Answer:

> What happened to the farm?

They generate deterministic domain features.

---

## Reward Engine

Answers:

> Was this state transition good or bad?

It compares states and evaluates the consequences of actions.

---

## Learning Model

Answers:

> Given this state, which action should be preferred?

It learns from the reward-labelled historical data.

Therefore:

```text
OBS
 ↓
Business Experts
 ↓
State Features
 ↓
Reward Engine
 ↓
Reward / Credit Assignment
 ↓
Training Dataset
 ↓
ML / RL Model
```

---

# 20. Reward should not necessarily equal profit

Profit is an important concept, but it may not be sufficient as the complete reward.

For example:

```text
Action A

cash ↓
assets ↑
net_worth ≈
```

This may be a good investment despite producing no immediate profit.

Similarly:

```text
Action B

cash ↑
assets ↓
net_worth ↓
```

may generate immediate liquidity while damaging the long-term position.

Therefore the reward should represent **economic progress**, not merely immediate profit.

---

# 21. Relative reward

Because different games may have different economic scales, reward should preferably be normalized.

Possible candidates:

```text
relative_cash_change
relative_net_worth_change
relative_asset_change
relative_inventory_change
```

For example:

```text
Δnet_worth_relative =
    Δnet_worth / previous_net_worth
```

This allows comparisons such as:

```text
+8% on 1,000
```

and:

```text
+8% on 100,000
```

without confusing the absolute scale.

---

# 22. Reward composition

A possible future reward formulation could be:

```text
reward =
    w_financial * financial_score
  + w_production * production_score
  + w_inventory * inventory_score
  + w_livestock * livestock_score
  + w_agriculture * agriculture_score
  + w_operations * operations_score
```

where the individual components are generated from deterministic state transitions.

However, the weights:

```text
w_financial
w_production
...
```

must not be chosen arbitrarily without validation.

This formulation is therefore a **candidate architecture**, not a final formula.

---

# 23. Immediate reward vs delayed reward

Two reward concepts should be distinguished.

### Immediate reward

Measures what happened directly after the action.

Example:

```text
BUY COW

cash ↓
animal assets ↑
net_worth ≈
```

---

### Delayed reward

Measures the future consequence.

Example:

```text
BUY COW
    ↓
CARE
    ↓
PRODUCTION
    ↓
SELL MILK
```

The economic benefit appears later.

A complete reward system may therefore need both:

```text
immediate reward
+
delayed reward
```

---

# 24. Reward horizon

A future question is how far into the future an action should be evaluated.

Possible horizons:

```text
next observation
next few turns
next day
next production cycle
end of game
```

Different actions may have different natural horizons.

For example:

```text
SELL PRODUCT
```

has an almost immediate financial effect.

Whereas:

```text
PLANT CROP
```

may require many turns before its economic contribution becomes observable.

The reward system should therefore investigate **action-specific temporal horizons**.

---

# 25. Causal chains

Some actions naturally form causal chains.

Examples:

```text
BUY SEED
 → PLANT
 → WATER
 → GROW
 → HARVEST
 → SELL
```

and:

```text
BUY ANIMAL
 → PLACE
 → FEED
 → CARE
 → PRODUCE
 → SELL
```

These chains are important because they provide a natural structure for reward attribution.

A future implementation may explicitly identify these chains.

---

# 26. Reward propagation

One possible strategy is to propagate a reward backward through a causal chain.

Conceptually:

```text
Economic result
       ↓
   SELL
       ↓
   HARVEST
       ↓
   PRODUCTION
       ↓
    CARE
       ↓
   PLANT / BUY
```

The further an action is from the result, the less reward it may receive.

However, temporal distance alone should not determine the reward.

An earlier action may be more important than a later one.

Therefore:

```text
reward ≠ purely temporal discounting
```

The system should combine:

```text
time
+
causal relevance
+
economic contribution
```

---

# 27. The role of negative rewards

Negative reward should not simply mean:

```text
cash decreased
```

because many valid investments reduce cash.

Negative reward should instead represent something closer to:

> **The action caused or contributed to an undesirable deterioration of the farm's state.**

Examples:

```text
wasted resources
unnecessary expense
asset destruction
avoidable production loss
poor timing
unproductive investment
loss of economic value
```

The distinction between:

```text
investment
```

and:

```text
loss
```

is therefore fundamental.

---

# 28. Reward should be explainable

One of the main design objectives is explainability.

For every reward, the system should ideally be able to answer:

```text
Why was this action rewarded?
```

Example:

```text
Action:
SELL WHEAT

Reward:
+0.083

Reason:
+ liquidity
+ net worth
+ inventory conversion
+ completed production cycle
```

Another example:

```text
Action:
BUY COW

Reward:
+0.012

Reason:
- liquidity
+ animal asset value
+ productive capacity
net worth approximately unchanged
```

This makes the reward system auditable.

---

# 29. Reward should be reproducible

Given the same:

```text
previous state
+
action
+
resulting state
```

the reward calculation should always produce the same result.

Therefore the first reward system should be:

```text
deterministic
```

This is consistent with the general architecture of the Business Experts.

Machine learning should learn from the reward signal.

The reward itself should not initially be learned.

---

# 30. Historical games and reward reconstruction

The historical Kaggriculture datasets provide sequences of observations and actions.

The proposed process is:

```text
Historical game
      ↓
Observation t
      ↓
Business Experts
      ↓
State t
      ↓
Action t
      ↓
Observation t+1
      ↓
Business Experts
      ↓
State t+1
      ↓
Reward Engine
      ↓
Immediate reward
```

Repeated for the complete game:

```text
t0 → reward0
t1 → reward1
t2 → reward2
...
t719 → reward719
```

This allows the historical games to be transformed into a training dataset.

---

# 31. Potential training record

A future training record could conceptually look like:

```text
state_features
action
next_state_features
reward
```

For example:

```text
{
    "state": {...},
    "action": "BUY_SEED",
    "next_state": {...},
    "reward": 0.018
}
```

For supervised learning, the reward may later become:

```text
target
```

or part of the target construction.

For reinforcement learning, it may become:

```text
reward_t
```

associated with:

```text
(state_t, action_t)
```

---

# 32. Supervised learning vs reinforcement learning

The reward-engineering work is useful for both approaches.

## Supervised learning

The reward can be transformed into a target representing the quality of an action.

For example:

```text
state → action_quality
```

or:

```text
state → expected_reward
```

---

## Reinforcement learning

The reward becomes part of the environment feedback:

```text
state
 ↓
action
 ↓
reward
 ↓
next_state
```

The model then learns a policy or value function.

Therefore the reward-engineering layer should ideally remain independent of the final learning algorithm.

---

# 33. Important hypothesis

The current central hypothesis is:

> **Kaggriculture may be better modeled by learning the quality and consequences of decisions than by directly predicting the winner of the game.**

The final winner may still be useful as an evaluation metric.

However, it should not necessarily be the only training signal.

---

# 34. Proposed conceptual model

The current conceptual model is:

```text
                  GAME HISTORY
                       │
                       ▼
                Raw observations
                       │
                       ▼
              Business Experts
                       │
                       ▼
                Semantic State
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        Action analysis      State change
             │                   │
             └─────────┬─────────┘
                       ▼
                 Reward Engine
                       │
                       ▼
              Reward Attribution
                       │
                       ▼
              Training Dataset
                       │
                       ▼
                 ML / RL Model
                       │
                       ▼
                    ACTION
```

---

# 35. Open questions

The following questions remain open and should be investigated before implementing the final reward system.

## 35.1 What exactly should the reward measure?

Possibilities include:

```text
economic progress
net worth improvement
productive capacity
future earning potential
liquidity management
combined economic state
```

---

## 35.2 How should liquidity and net worth be combined?

Possible approach:

```text
financial_reward =
    f(
        Δliquidity,
        Δnet_worth
    )
```

But the exact function remains undefined.

---

## 35.3 How should investments be rewarded?

For example:

```text
BUY_COW
BUY_SEED
BUY_LAND
BUILD_COOP
BUILD_PASTURE
```

should not necessarily receive a negative reward simply because cash decreases.

---

## 35.4 How should delayed effects be attributed?

For example:

```text
PLANT
```

may only become profitable much later.

The system must determine how much of the future reward belongs to the planting action.

---

## 35.5 How should multiple actions share one result?

If five actions are necessary to produce one harvest, how should the reward be distributed among them?

---

## 35.6 How should failed strategies be represented?

Losing games are potentially valuable.

A failed investment sequence may teach the model:

```text
what not to do
```

Therefore both successful and unsuccessful trajectories should potentially contribute to training.

---

## 35.7 Should reward depend on the final game result?

Current hypothesis:

```text
Not necessarily.
```

The final result can remain an evaluation metric without being the primary reward.

---

# 36. Initial design principles

The current brainstorming suggests the following principles.

### Principle 1

**Do not use absolute liquidity as the target.**

---

### Principle 2

**Do not assign the entire reward to the final action.**

---

### Principle 3

**Evaluate state transitions, not only final states.**

---

### Principle 4

**Distinguish cash movement from economic gain or loss.**

---

### Principle 5

**Investments that reduce liquidity are not automatically bad.**

---

### Principle 6

**Net worth and liquidity should be evaluated together.**

---

### Principle 7

**Use normalized/relative changes where appropriate.**

---

### Principle 8

**Delayed consequences must be considered.**

---

### Principle 9

**Reward attribution should consider causal contribution, not only temporal distance.**

---

### Principle 10

**The first reward engine should be deterministic and explainable.**

---

### Principle 11

**Business Experts provide the semantic information needed by the reward engine.**

---

### Principle 12

**The reward engine should remain independent from the final ML/RL algorithm.**

---

# 37. Current working hypothesis

The current working hypothesis can be summarized as:

```text
The target is not:

    "How much money did the farm finish with?"

The target is not necessarily:

    "Did the farm win?"

The target is closer to:

    "How much did this decision contribute to improving
     the economic and productive trajectory of the farm?"
```

Therefore:

```text
                    ACTION
                       │
                       ▼
              State transition
                       │
                       ▼
          Economic / operational impact
                       │
                       ▼
             Reward calculation
                       │
                       ▼
             Credit assignment
                       │
                       ▼
            Action quality signal
```

---

# 38. Next development phase

Before implementing the final reward function, the following steps should be performed.

## Step 1 — Define state deltas

Identify exactly which features are compared between:

```text
state_t
```

and:

```text
state_t+1
```

---

## Step 2 — Define economic transition categories

Create deterministic rules for cases such as:

```text
liquidity ↓ / net_worth ≈
liquidity ↓ / net_worth ↑
liquidity ↓ / net_worth ↓
liquidity ↑ / net_worth ↑
liquidity ↑ / net_worth ≈
liquidity ↑ / net_worth ↓
```

---

## Step 3 — Identify causal action chains

Examples:

```text
seed → planting → care → harvest → sale
```

```text
animal → placement → care → production → sale
```

---

## Step 4 — Define reward attribution

Determine how a final improvement is distributed among the actions that contributed to it.

---

## Step 5 — Normalize the reward

Determine an appropriate reward scale, for example:

```text
[-1, +1]
```

or another normalized range.

---

## Step 6 — Test on historical games

Apply the deterministic reward engine to real historical trajectories.

Do not train a model yet.

First inspect:

```text
reward distribution
reward by action
reward by game
reward by winning/losing game
```

---

## Step 7 — Validate against human reasoning

Inspect whether the reward system agrees with obvious examples:

```text
good investment
bad investment
productive action
wasted action
successful production chain
failed production chain
```

---

## Step 8 — Only then select the learning strategy

After the reward signal is stable, decide whether to use:

```text
supervised learning
```

or:

```text
reinforcement learning
```

or potentially a hybrid approach.

---

# 39. Final conceptual objective

The long-term objective is to create a learning system that does not merely memorize:

```text
"winning games look like this"
```

but learns:

```text
"given this state,
this action tends to improve the farm's future position."
```

The desired learning process is therefore:

```text
OBSERVATION
    ↓
UNDERSTANDING
    ↓
ACTION
    ↓
CONSEQUENCE
    ↓
REWARD
    ↓
CREDIT ASSIGNMENT
    ↓
LEARNING
    ↓
BETTER ACTION
```

The central research question is:

> **Can a deterministic, explainable reward and credit-assignment mechanism transform historical Kaggriculture trajectories into a meaningful learning signal without relying exclusively on the final game outcome?**

This question should be answered experimentally before committing to the final ML/RL architecture.
