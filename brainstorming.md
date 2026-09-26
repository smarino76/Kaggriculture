# Kaggriculture: Brainstorming

Each player starts with an empty farm and a small amount of income (seed money, if you will). Each turn, they can perform actions such as moving around the board, purchasing seeds or livestock, planting seeds, watering plants, harvesting produce or animal products, and selling that produce at the market. The game runs for a fixed amount of time representing one season, and the winner is determined by who has the most money in the bank at the end.


## Object Types

Type	Yield Type	Seed Cost	Base Market Price	Time to First Yield	Time to Max Yield	Subsequent Yields	Max Yield	Action Cost	Yield / tile / day
Wheat	One-time	10	25	2 days	4 days	none	6 (4 unfertilized)	1	0.80
Carrot	One-time	20	35	2 days	3 days	none	4 (3 unfertilized)	1	0.75
Tomato	Ongoing	50	60	8 days	11 days	every day ×4	4	1	0.33
Strawberry	Ongoing	100	120	10 days	16 days	every other day ×4	4	1	0.24
Melon	One-time	80	250	10 days	10 days	none	6	1	0.55
Goose/Egg	Ongoing	300	50	4 days	NA	every day, indefinitely	4 held	1 + 1 (build coop)	1.00
Cow/Milk	Ongoing	400	160	8 days	NA	every two days, indefinitely	6 held	1 + 1 (build pasture)	0.50
Sheep/Wool	Ongoing	500	200	6 days	NA	every three days, indefinitely	6 held	1 + 1 (build pasture)	0.33
Fertilizer	NA	100	X		X	X		1	



For crops, "Yield / tile / day" is total units harvested divided by the days the tile is occupied, watering daily and harvesting at peak yield. For animals it is the steady-state production rate (1 / interval) once the first yield lands; animals keep producing for as long as they are fed, so there is no fixed occupancy to divide by. "Max Yield" for animals is max_held, the cap on unharvested product sitting on the tile, not a lifetime total.

Crop "Time to Max Yield" is the age at which yield stops increasing under daily watering, which is not always the end of the bonus window:

Melon's bonus window is ages 6–12, but base 1 plus one unit per watered day reaches the cap of 6 at age 10, so ages 11–12 add nothing. Fertilizing reaches the cap at age 8.
Wheat and Carrot only reach their listed Max Yield of 6 and 4 with fertilizer; watering alone peaks at 4 and 3.
Tomato and Strawberry are ongoing but not indefinite: production is capped at 4 scheduled yields (tomato at ages 8–11, strawberry at ages 10, 12, 14, 16), after which the plant decays into a weed.
All plants must be watered every day. They will turn into weeds if they are not watered for two successive days. All animals must be fed every day using wheat. They will escape and be unrecoverable if they are not fed for two successive days. Wheat is also available to buy at the market and can be purchased at the current market price.

## Actions

Each turn, the player may take one action. There are 24 turns per day, and 30 days in the season - 720 total turns.

Farmer / Farm Hand Action
Each Farmer / Farm Hand can be given an action every turn. Farmer/Farm Hand CAN occupy the same space.

### Movement

NORTH, SOUTH, EAST, WEST — Move one cell in that direction. Moves off the edge of the board are no-ops. Locked tiles are passable: a unit may move onto and across unbought quadrants, but tile actions (PLANT, WATER, BUILD_*, etc.) all no-op on a locked tile and consume nothing. The exception is the shed actions PICKUP, DROP, and PLACE-into-shed, which work from any shed-access tile even while that tile is locked — they use the tile only as a standing position and never change it.
### Shed

Picks up an item from the shed (must be orthogonally adjacent) into the inventory

PICKUP <item> [n] — move up to n of <item> (default 1) from the shed into the active farmer/hand's inventory. Any item present in the shed is valid (animals, fertilizer, harvested produce, etc.). Seeds live in a separate slot and are never picked up — PLANT consumes them directly.
DROP — orthogonally adjacent to the shed, dump the active farmer/hand's entire current inventory into the shed. Overflow past shedCapacity is discarded. No-op if not shed-adjacent.
### Plants

PLANT — Plant a seed purchased from the market
Seeds are automatically available to all Farmers / Farm Hands
If you try to plant too many in a specific turn, none are planted
ie if you have 1 melon seed, but two units do the PLANT MELON command
WATER — Water a plant. This only needs to be done once per day, and subsequent waterings on the same day are a no-op.
HARVEST — Gather produce from a plant. If the plant does not have subsequent yields, it will be removed from the map. Each harvest action will yield at least one unit of the crop, with the potential of additional yield depending on watering and fertilizer (the formula differs by crop type — see harvest yields below). Harvested items are added to the inventory.
FERTILIZE — Fertilize a plant to increase its potential yield (see harvest yields below).
Doubles the per-day yield bonus for the next 3 days. The bonus only applies on days the plant is also watered (basic needs first).
### Animals

PLACE <item> [n] — Drop items from the active farmer/hand inventory into either a tile or the shed:
Animal placement: standing on a matching unoccupied structure (GOOSE on a coop, SHEEP/COW on a pasture) places one animal from inventory onto the tile. The n argument is ignored.
Shed drop: standing orthogonally adjacent to the shed moves up to n (default 1) of <item> from inventory into the shed. Capped by shedCapacity; excess stays in inventory.
FEED — Feed an animal using wheat (only needs to be done once per day)
HARVEST — Collect the eggs/milk/wool produced by the animal.
COLLECT_FERTILIZER — Collect 1 fertilizer from the animal. Every surviving animal makes 1 available at the end of each day, whether or not it was fed or cared for. Uncollected fertilizer does not accumulate, so an animal left alone for five days still yields 1 unit.
CARE — Care for an animal (once per day, no-op if already cared for). See animal care below.
### Animal Care

CARE banks a yield bonus that is paid out on the animal's next scheduled production:

At end of day, if the animal was both fed AND cared for that day, pending_care_bonus increments by 1. Days where the animal was unfed do not bank a bonus (basic needs first).
On a scheduled production day, if the animal is fed, the entire banked bonus is added to that production's yield (in addition to the base 1) and the bank resets to 0.
If the animal is unfed on the production day, the base 1 unit is still produced, but the banked bonus is not applied and the bank resets to 0.
pending_care_bonus is capped indirectly by the per-animal max_held cap on yield_units.
### Terrain

BUILD_COOP - adds a coop to an unoccupied tile
BUILD_PASTURE - add pasture to an unoccupied tile
DIG — Remove a plant from a square to free up space OR remove a weed from a square (does not yield any produce) OR remove an empty goose coop / pasture. A coop or pasture with an animal on it cannot be dug; the DIG is a no-op.
### Other

PASS — Default if there is nothing to do (optional)
### Market Action

Each turn you can submit up to maxMarketOrdersPerTurn (default 10) market actions; any orders past that limit are silently dropped. This is an ordered list and market orders will be processed in order simultaneously (one from each player) while both players have orders.

BUY_SEED — Purchase N units of a single item from the market.
BUY_SEED WHEAT 1
BUY_ANIMAL -
BUY_ANIMAL GOOSE 1
BUY_PRODUCT
BUY_PRODUCT WHEAT 1
BUY_PRODUCT FERTILIZER 1
SELL — Sell N units of a single item to the market.
SELL WHEAT 1
HIRE — Hire a farm hand for the day. Cost increases for each extra hand hired on the same day.
BUY_LAND - unlock a new 5x5 segment of land to plant on. Increasing in cost.
Costs are: $1k, $2k, $4k
## Watering / Animal Feed

Plants (and animals) must be watered/fed a minimum of every other day. Watering only needs to be done once per day, and subsequent watering actions are a no-op. In the case of plants not watered for two consecutive days, at the end of the day they turn into a WEED. In the case of animals they escape (unrecoverable).

A new seed starts with consecutive_unwatered = 1 — the planting day itself counts as the first missed day. A seed planted and left unwatered that same day reaches 2 at the end-of-day refresh and becomes a weed that night, before it grows. There is no grace period for fresh plantings.

A newly placed animal starts with consecutive_unfed = 0, so it survives its first day unfed.

Note that watering one-time yield plants during their yield window results in a higher yield. This is NOT true for ongoing yield plants/animals. See below.

## Harvest Yields

Plants will potentially have higher yields based on how well they have been cared for.

One-time crops (wheat, carrot, melon): Starting at half the plant's max_yield_day (Time to Max Yield) rounded up, watering during the bonus window will add one unit per day to the total harvestable yield.
Fertilized plants add 2 per day instead.
Ongoing crops (tomato, strawberry): Scheduled production happens at fixed intervals. The base yield is 1 per scheduled production. If the plant is fertilized AND watered that day, yield is doubled to 2.
Once a plant has hit its maximum lifespan, the total yield available on the plant will reduce by 1 every other turn until it hits 0, at which point the plant becomes a weed.
One-time crops reach max lifespan one day after max_yield_day.
Ongoing crops start decay one day after their cumulative production count reaches max_yield (i.e. they've fired enough scheduled productions to hit the cap, regardless of whether the produce has been harvested).
## Map Features

Each player has their own farm with a set number of squares. Players are unable to see the state of the other’s shed, but can see the state of their opponent’s farm.

### Farm Space

The land near your farm is a boardSize × boardSize grid (default 10×10), divided into four 5×5 quadrants. At first, your farm covers one quadrant (25% of the squares). For an increasingly large fee, you can buy the neighboring quadrants and eventually cover 100% of the squares.
Each plant or animal occupies one square on the farm.
Players can allocate these squares however they choose between crops and livestock. There are no specific limits per type.
Weeds have a chance of spawning on any empty cells on the farm, and must be cleared before the land can be used for other purposes.
Squares on the farm can be either a plant, a coop/pasture, a weed, or empty.
### Shed (Inventory)

Functions as an inventory for items that are harvested but not yet sold, or for seeds that have not yet been planted
Farmer and hired farm hands will spawn at the shed at the start of each day
Farmer and hired farm hands drop their inventory at the end of the day in the shed (if there is room)
Limited to 100 items, excluding seeds. Once the shed is full, any further items added (via PLACE mid-day or end-of-day inventory drop) are discarded — there is no overflow holding area, so stockpiling on farmer/hand inventories does not bypass the cap.
The shed sits at the center of the board and is not a tile — it never appears in the tiles array, whose only values are None, "LOCKED", and structure dicts. "Orthogonally adjacent to the shed" means standing on one of the four center tiles, (half-1, half-1), (half, half-1), (half-1, half), (half, half) for half = boardSize // 2. At the default boardSize = 10 those are (4,4), (5,4), (4,5), and (5,5), one in each quadrant. Since only NW starts unlocked, three of those four tiles begin locked; the shed is reachable from all of them regardless, because the shed itself is never locked.

### Farmer/Farm Hand

### Hiring

Hiring is a market order (HIRE). It costs more every time you want to hire an additional hand each day. At the end of the day all, hands drop inventory at the farm and disappear (need to be re-hired each day)
Cost is farmHandCostMult * fib(n) where n is the number of hires already made today (fib starts 1, 1, 2, 3, 5, 8, 13, …).
With the default farmHandCostMult = 1: 1, 1, 2, 3, 5, 8, 13, 21, etc… (resets at the start of each day)
A hired hand appears orthogonally adjacent to the shed in a free space following NWSE. If there are not open spaces, it looks for the one with the least occupants, breaking ties by NWSE preference
Spawn placement ignores whether the tile is locked. Since the main farmer starts on (4,4), the least-occupied rule sends the first hire of each day to (5,4), which is locked until the NE quadrant is bought. Locked tiles are passable, so a hand spawned on one can move back to unlocked land.
### Inventory

When harvesting or picking items up, they are added to inventory.
Can drop items in the shed
At the end of the day, all items in all inventory will be added to shed inventory (if there is room). Anything that doesn't fit is discarded — overflow is lost.
## Town Buildings

As the season progresses, new shops unlock at regular intervals (every townShopUnlockInterval days, default 3). Each unlock is drawn uniformly at random with replacement from the full shop table, so the same shop can unlock more than once — a season might end up with three bakeries and no yarn store. Once unlocked, a shop stays active for the rest of the game, and unlocking stops after 8 total instances. Total demand grows monotonically as more shops unlock.

Each unlocked shop instance consumes one of every product it demands every townShopSellInterval turns (default 4). So with the default interval, a shop demanding wheat removes 6 wheat from the market per day, and two copies of that shop remove 12. Single-product shops consume 2x.

In addition, the town center consumes one of every product (excluding fertilizer) every townCenterSellInterval turns (default 24, i.e. once per day). This rate is flat for the whole season — it does not ramp.

Shop Type	Increases Demand For
Bakery	eggs, wheat
Pizza Shop	milk, tomatoes, wheat
Brunch Spot	eggs, wheat, strawberries
Yarn Store	wool (2x)
Ice Cream Shop	strawberries, milk, wheat
Pet Cafe	carrots (2x)
Smoothie Shop	strawberries, milk
Farmers Market	wheat, carrots, tomatoes, strawberries
## Market Mechanics

The market has an unlimited supply of seeds and animals at fixed prices. Sell prices, however, move dynamically per resource and persist across days.

Every product (and fertilizer) starts the game with a market inventory of I0 = 10,000 units, far above any single game's realistic production volume so that inventory is essentially guaranteed to stay positive. The sell price for a product is base at I0, rises as inventory falls (players buying or town consumption draining supply), and falls as inventory grows (players selling).

Selling inventory to the market
Players can queue any number of sell or buy orders (for any quantity) in the market action list. Orders are processed concurrently across players, one unit at a time. For example, when both players issue SELL CARROT 10 first, we take the current carrot price, give both players that price for their first carrot, then add 2 carrots to the market (1 from each player) — which may shift the price — and repeat until both orders complete.

If the sell price has been driven down to $1 (the price floor), the unit is still purchased but is not added to market inventory, so the floor remains responsive to subsequent buys.

Buying inventory from the market
Only WHEAT and FERTILIZER can be bought from the market via BUY_PRODUCT (other products are sold at the market but not bought back). Selling is unrestricted: every product, including fertilizer collected from animals, can be sold via SELL. Two things drain market inventory: town buildings (town center and shops, which consume products for free) and player BUY_PRODUCT orders. Buy orders follow the same one-unit-at-a-time concurrent procedure as sell orders. If a player runs out of money mid-order, the order is stopped.

The buy price is quoted at the post-buy inventory and the sell price is quoted at the pre-sell inventory, so an immediate buy followed by a sell of the same item against an otherwise-unchanged market nets exactly zero.

## The Price Function

For each resource the curve is defined by a base price, an anchor throughput T, and an independent shape function + target move for each side of the equilibrium:

price(inv) = base + sign · amp · f(|inv − I0|)
  sign = +1  if inv < I0   (scarcity → price up)
  sign = −1  if inv > I0   (glut    → price down)
  amp  = target · base / f(T)        (derived; not stored)
  f    ∈ { linear, sq, sqrt, log, log10, hinge }   (log uses ln(1+x), so f(0)=0)
Floored at $1 and rounded to the nearest dollar.

hinge is the one shape that depends on T rather than on x alone: with u = x / T it evaluates to u + 8 · max(0, u − 1)². Below T it is linear in u; above T the quadratic term takes over and the price climbs steeply. Since f(T) = 1 by construction, target keeps its usual meaning.

T is the production capacity of a single 5×5 field over a 24-day window at optimal watering with no fertilizer (animal totals are pre-discounted by 30% to account for wheat-feed overhead, and allow one day to build the coop or pasture). The 24-day window is a calibration horizon, not the 30-day season length. It is shorter on purpose: the opening days are setup-heavy and yield little.

target says "moving T units past I0 shifts the price by target × base." Picking different f and target on each side lets resources with similar production profiles play very differently strategically — wheat panics on scarcity but absorbs gluts; melon barely reacts to scarcity but crashes hard on overproduction; wool mirrors melon at a smaller scale. Premium resources (base > $100: strawberry, melon, milk, wool) use above_target > 1, so even modest gluts drive them straight to the $1 floor — bundling and timing sales matters more for these than for staples.

Carrot, tomato and egg use hinge on the scarcity side, so their prices stay near base under ordinary demand and rise sharply once demand runs past T. The town shops that consume them are listed in unlocked_shops.

Carrot — hinge at below_target 1.00. Consumed by pet cafes (single-product, so each consumes double) and farmers markets.
Tomato — hinge at below_target 0.40. Consumed by pizza shops and farmers markets.
Egg — hinge at below_target 0.40. Consumed by bakeries and brunch spots.
Tomato and egg keep the below_target of the linear curves they replaced. Because linear's amplitude already normalises to x / T, which is exactly hinge's below-knee branch, their prices from I0 down to I0 − T are unchanged; the curves differ only past the knee.

Resource	Base	I0	T	Below func	Below target	Above func	Above target	P(I0−T)	P(I0+T)	P(I0+2T)
Wheat	25	10,000	400	sqrt	0.80	log	0.20	$45	$20	$19
Carrot	35	10,000	450	hinge	1.00	sqrt	0.70	$70	$10	$1
Tomato	60	10,000	200	hinge	0.40	sqrt	0.60	$84	$24	$9
Strawberry	120	10,000	100	sqrt	0.70	linear	1.60	$204	$1	$1
Melon	250	10,000	300	log	0.20	sq	3.60	$300	$1	$1
Egg	50	10,000	332	hinge	0.40	log	0.20	$70	$40	$39
Milk	160	10,000	122	sqrt	0.60	linear	1.60	$256	$1	$1
Wool	200	10,000	105	log	0.20	sq	3.20	$240	$1	$1
Fertilizer	100	10,000	200	linear	0.40	linear	0.40	$140	$60	$20
The defaults live in MARKET_PARAMS in kaggriculture.py. Per-resource overrides (sparse: any subset of base, I0, T, below_func, below_target, above_func, above_target) can be supplied at episode creation via env.configuration["marketParams"] without touching code, e.g. {"WOOL": {"above_target": 0.95}}.

## Turn Processing Order

Action validation — verify action legality
Player actions — record the actions taken by each player (happening simultaneously)
Market actions - process market queue in order by player (described above)
Town buy actions - town center and shops reduce inventory
Update observations
Day refresh — if applicable, update the condition of plants and animals for a new day, and reset their fed/watered to condition to false
Market refresh — modify the price of items on the market based on sells from previous turn
Income update — update the player’s bank based on any buys or sells
Farm update — clear plants that have been harvested, items from the inventory that have been used or sold, add new plants/animals to the farm, etc
## Win Conditions

The win condition is simple- whoever has the greatest number of coins at the end of the season is the winner. It is also possible that the two players will tie.

## Reward

The player who has the most money in the bank at the end of the game wins. Unsold items in the inventory do not count towards that total.

## Observation Format

The top-level observation passed to each agent:

{
  "player": int,           # 0 or 1
  "day":    int,           # 0-indexed in-game day
  "hour":   int,           # 0-indexed turn within the day
  "farms":  [farm, farm],  # public per-player state, indexed by player id (shared)
  "market": {              # shared
    "inventory": { "WHEAT": int, "CARROT": int, ... },
    "prices":    { "WHEAT": int, "CARROT": int, ... },
  },
  "town": {                # shared
    "unlocked_shops": ["BAKERY", "BAKERY", ...],   # may repeat; each entry consumes independently
  },
  "private": {             # this player only; opponent's private state is not visible
    "shed":        { "WHEAT": int, "GOOSE": int, "FERTILIZER": int, ... },
    "seeds":       { "WHEAT": int, "CARROT": int, ... },
    "inventories": [farmer_inv, hand_inv, ...],  # [0] is the main farmer
  },
}
Each farm dict (public, visible to both players):

{
  "money":              float,
  "tiles":              [[tile, ...], ...],   # tiles[y][x]
  "farmer":             [x, y],
  "hands":              [[x, y], ...],         # hired hands for the current day
  "unlocked_quadrants": ["NW", ...],          # subset of {"NW","NE","SW","SE"}
  "hires_today":        int,                  # used to price the next HIRE
}
A tile is one of:

None — empty unlocked tile
"LOCKED" — tile in a quadrant the player has not yet bought
a plant dict:
  {
    "kind":                 "PLANT",
    "crop":                 "WHEAT" | "CARROT" | "TOMATO" | "STRAWBERRY" | "MELON",
    "planted_day":          int,
    "watered_today":        bool,   # reset to False each end-of-day
    "consecutive_unwatered": int,   # 2+ → tile turns to a weed
    "yield_units":          int,    # units currently harvestable
    "max_lifespan_step":    int,    # step at which decay begins; -1 for ongoing crops
    "fertilized_until_day": int,    # last day fertilizer bonus applies; -1 if none
  }
a weed dict: {"kind": "WEED"}
an animal structure dict (coop/pasture, optionally occupied):
  {
    "kind":                 "COOP" | "PASTURE",
    "animal":               "GOOSE" | "COW" | "SHEEP" | None,  # None until PLACEd
    "placed_day":           int,
    "yield_units":          int,
    "fed_today":            bool,
    "consecutive_unfed":    int,    # 2+ → animal escapes
    "cared_today":          bool,
    "fertilizer_available": bool,   # set at end-of-day for every surviving animal; cleared by COLLECT_FERTILIZER
    "pending_care_bonus":   int,    # banked CARE bonus, applied on the next yield tick
  }
## Quick Start

```python
from kaggle_environments import make


def my_agent(obs):
    # Buy one wheat seed on the very first turn, then PASS forever after.
    if obs.get("step", 0) == 0:
        return {"farmer": ["PASS"], "market": [["BUY_SEED", "WHEAT", 1]]}
    return {"farmer": ["PASS"], "market": []}


env = make("kaggriculture", configuration={"episodeSteps": 200})
env.run([my_agent, "random"])
env.render(mode="ipython", width=800, height=800)
```

## Configuration Defaults

Per-crop seed costs and per-product base prices are not configurable; they are documented in the Object Types and Price Function tables above. The configurable knobs are:

Parameter	Default	Description
episodeSteps	720	Total turns in the season (24 turns × 30 days)
boardSize	10	Width and height (in tiles) of each player's square farm. Advanced uses 10 = four 5x5 quadrants
startingMoney	3000	Coins each player starts with
maxMarketOrdersPerTurn	10	Maximum number of market orders processed per player per turn; extras are silently dropped
turnsPerDay	24	Number of turns that make up one in-game day
shedCapacity	100	Max non-seed items the shed can hold; overflow at end-of-day drop is discarded
weedSpawnChance	0.005	Per-tile probability of a weed spawning on an empty unlocked tile during end-of-day refresh
townShopUnlockInterval	3	Days between successive town shop unlocks (drawn with replacement, capped at 8 instances)
townShopSellInterval	4	Turns between consumption ticks by every unlocked town shop instance
townCenterSellInterval	24	Turns between consumption ticks by the town center (flat rate, once per day)
seed	null	Optional input seed for deterministic episode generation; cleared from config after read so it stays out of agent observations




## Resumen del juego


Cada jugador administra una granja y gana quien termina con más dinero en el banco. Las acciones se dividen en:

Acciones físicas del granjero y trabajadores: mover, plantar, regar, fertilizar, cosechar, construir, alimentar, cuidar, vender al almacén, etc.
Órdenes de mercado: comprar semillas, animales, trigo, fertilizante, vender productos, contratar trabajadores y comprar terreno.
Gestión temporal: las plantas y animales requieren cuidados diarios y tienen ventanas de producción.
Competencia indirecta: ambos jugadores comparten mercado, precios, inventario del mercado y demanda de la ciudad.
El dinero de los productos almacenados no cuenta al final, por lo que el agente debe decidir cuándo vender y no solamente cuánto producir.

## Datos disponibles para el agente


En cada observación puede conocer:

Día y hora del episodio.
Su propia información privada:
Dinero.
Semillas.
Contenido del almacén.
Inventario de cada granjero o trabajador.
Estado público de ambas granjas:
Plantas, animales, estructuras y malas hierbas.
Posiciones de jugadores y trabajadores.
Terreno desbloqueado.
Número de trabajadores contratados ese día.
Dinero de ambos jugadores.
Mercado compartido:
Inventario.
Precios actuales.
Ciudad:
Tiendas desbloqueadas y su demanda.
No puede ver el almacén privado del oponente.
Esto permite inferir bastante sobre el rival: cultivos, animales, ritmo de expansión, posiciones, ventas indirectas y posible estrategia, aunque no sus reservas exactas.

## Puntos estratégicos importantes

1. La planificación temporal domina el juego
Plantar tarde puede ser inútil. Por ejemplo:

Wheat y carrot producen rápido.
Tomato y strawberry necesitan más días, pero generan varios rendimientos.
Melon tiene una producción única muy valiosa.
Los animales requieren inversión inicial, estructura, alimento y cuidados continuos.
El agente debe valorar el beneficio restante hasta el día 30, no solo la rentabilidad teórica completa.

2. La capacidad de acción es un recurso
Cada trabajador puede hacer una acción por turno. Contratar manos cuesta poco al principio, pero el coste sigue la sucesión de Fibonacci durante el día.

Por tanto, hay que decidir si las manos se usan para:

Regar.
Alimentar y cuidar animales.
Plantar.
Cosechar.
Mover productos.
Transportar inventario.
Construir o limpiar terreno.
La posición también importa. Moverse consume turnos, y el almacén está en el centro, pero ciertos tiles centrales pueden estar bloqueados aunque sigan siendo utilizables para acceder al almacén.

3. El cuidado correcto tiene detalles fáciles de perder
Una planta nueva empieza con un día de falta de riego.
Una planta plantada y no regada ese día puede convertirse en maleza durante la primera noche.
Un animal nuevo empieza con consecutive_unfed = 0, así que tiene una tolerancia distinta.
Regar y alimentar solo hace falta una vez al día.
Cuidar animales genera un bonus acumulado, pero solo se aplica en la siguiente producción programada.
Fertilizar no siempre aumenta el resultado de la misma forma:
En cultivos de una sola cosecha duplica el bonus diario durante tres días.
En tomate y strawberry duplica la producción programada si están fertilizados y regados ese día.
En animales no aparece como acción de fertilización directa, sino como producto producido por ellos.
4. El mercado es parte central de la estrategia
Los precios dependen del inventario compartido. Esto introduce varias decisiones:

Vender producto inmediatamente o esperar.
Vender por lotes pequeños para evitar hundir el precio.
Observar la producción del rival mediante las variaciones del mercado.
Comprar wheat para alimentar animales cuando sea rentable.
Comprar fertilizante en vez de producirlo.
Anticipar el consumo de la ciudad.
Los productos premium, como melon, strawberry, milk y wool, son especialmente peligrosos: una sobreoferta puede llevar rápidamente el precio a $1. El dataset debería representar explícitamente la diferencia entre:

Valor potencial de producir.
Valor esperado después del impacto en el precio.
Dinero realmente obtenido tras vender.
5. La demanda de la ciudad cambia progresivamente
Cada tres días se desbloquea una tienda aleatoria, con repetición. Eso significa que una partida puede tener mucha demanda de wheat y eggs, pero poca de wool, por ejemplo.

La demanda observable puede servir para adaptar la estrategia:

Bakery y brunch favorecen eggs.
Pizza favorece milk y tomatoes.
Yarn store favorece wool.
Pet Cafe favorece carrots.
Farmers Market crea demanda amplia.
Ice Cream Shop y Smoothie Shop favorecen strawberries y milk.
## Cómo construiría el dataset

Yo separaría el dataset en tres niveles.

Nivel 1: decisiones locales
Cada muestra representa una decisión de acción:

Observación actual.
Acción elegida.
Acción legal o inválida.
Resultado inmediato.
Recompensa inmediata aproximada.
Próxima observación.
Aquí aprenderíamos tareas básicas:

Qué hacer cuando hay una planta lista.
Cuándo regar o alimentar.
Cómo llegar al almacén.
Cuándo cosechar.
Cómo usar trabajadores.
Qué acciones son inútiles o peligrosas.
Nivel 2: decisiones económicas
Cada muestra debería incluir variables derivadas:

Dinero actual y dinero al inicio del día.
Coste de semillas, animales, terrenos y trabajadores.
Inventario del almacén.
Precio actual y tendencia reciente de cada producto.
Días restantes.
Producción esperada antes del final.
Coste estimado de alimentar animales.
Valor liquidable del inventario.
Impacto esperado de vender una cantidad determinada.
La etiqueta no debería ser solo “ganar o perder”. Conviene almacenar objetivos intermedios, por ejemplo:

Dinero al final del día.
Beneficio de una plantación.
Valor de una venta.
Productos desperdiciados.
Animales perdidos.
Capacidad de almacén desperdiciada.
Precio medio obtenido.
Nivel 3: estrategia de episodio
Para cada episodio completo guardaríamos:

Configuración.
Semilla.
Estado inicial.
Secuencia completa de observaciones y acciones.
Resultado final.
Dinero final.
Inventario no vendido.
Producción total.
Ventas totales.
Terreno desbloqueado.
Número de animales perdidos.
Número de plantas convertidas en maleza.
Uso de trabajadores.
Evolución de precios.
Este nivel sirve para aprender planificación de largo plazo y no solo reacciones inmediatas.

## Qué tipos de partidas necesitamos generar

Para que el dataset no quede sesgado hacia una única forma de jugar, convendría generar partidas con:

Estrategia de cultivos rápidos.
Estrategia de melon.
Estrategia de cultivos recurrentes.
Estrategia animal.
Estrategia mixta.
Compra temprana de terreno.
Muchos trabajadores.
Muy pocos trabajadores.
Uso intensivo de fertilizante.
Venta inmediata.
Acumulación y venta por lotes.
Oponente pasivo.
Oponente agresivo con mucha producción.
Diferentes secuencias de tiendas desbloqueadas.
Precios de mercado modificados mediante marketParams.
También conviene incluir partidas deliberadamente malas para aprender de los errores:

Plantar sin poder regar.
Comprar animales sin capacidad de alimentarlos.
Llenar el almacén sin vender.
Vender productos premium en plena sobreoferta.
Contratar demasiadas manos.
Comprar terreno demasiado tarde.
Cosechar después de la ventana óptima.
Ignorar las malas hierbas.
## Recompensa recomendada para estudiar

La recompensa final debe seguir siendo el dinero bancario al terminar, pero para entrenar o analizar estrategias podemos usar métricas auxiliares:

Cambio de dinero por día.
Beneficio neto de cada activo.
Penalización por desperdicio.
Penalización por plantas perdidas.
Penalización por animales escapados.
Coste de acciones de movimiento.
Precio medio de venta.
Valor de oportunidad de no vender.
No mezclaría automáticamente estas métricas con la recompensa oficial sin experimentar, porque una bonificación intermedia podría enseñar al agente a maximizar ingresos diarios y perjudicar su resultado final.

## Preguntas que deberíamos resolver en la reunión

¿El objetivo inicial es imitar una política experta, entrenar por refuerzo, o construir primero un dataset para análisis?
¿Podemos ejecutar muchas partidas y controlar la semilla?
¿El agente verá únicamente la observación actual o también un historial?
¿Queremos que aprenda contra un oponente fijo, contra un agente aleatorio o contra una población de oponentes?
¿La acción se representa como una sola acción por trabajador más una lista de órdenes de mercado?
¿Queremos entrenar primero decisiones de alto nivel, como “invertir en animales”, o directamente acciones de bajo nivel, como mover y regar?
¿Necesitamos registrar también acciones inválidas y acciones que son válidas pero no producen ningún efecto?
## Mi propuesta inicial sería trabajar por fases:


Definir con precisión el formato de una muestra.
Construir una taxonomía de estrategias y errores.
Generar episodios variados y deterministas.
Analizar qué variables explican mejor la victoria.
Entrenar primero un modelo de decisiones de alto nivel.
Añadir después el control táctico de movimiento, riego, alimentación y almacén.





## Las reglas


Qué acciones existen.
Qué acciones son legales según la posición y el estado.
Costes, tiempos y requisitos.
Cómo cambian plantas, animales, mercado y dinero.
Qué consecuencias tienen los errores.
## A jugar


Observar el estado actual.
Elegir acciones.
Recibir el resultado.
Aprender qué decisiones aumentan la probabilidad de ganar.
Para esto, el dataset debería contener principalmente trayectorias de juego:


No conviene etiquetar cada muestra con “esta es la mejor estrategia” desde el principio. El agente debería descubrir estrategias mediante muchas partidas, explorando:

Cultivos rápidos y lentos.
Animales.
Fertilizante.
Contratación de trabajadores.
Compra de terreno.
Momento de vender.
Gestión del almacén.
Competencia por el mercado.
Errores y acciones inválidas.
La recompensa principal debe ser el resultado final: dinero en el banco al terminar. Las recompensas intermedias pueden ayudar a aprender, pero sin imponer demasiado una estrategia específica.

La separación más importante sería:

Capa de reglas: aprende qué ocurre cuando ejecuta una acción.
Capa de juego: aprende qué acción elegir para ganar.

El entorno ya funciona como generador de datos de reglas. Cada transición observación-acción-siguiente observación enseña las consecuencias reales. Para aprender a jugar necesitaremos después partidas contra oponentes variados, idealmente incluyendo agentes aleatorios, agentes sencillos y versiones anteriores del propio agente.

También hay que decidir si el agente podrá usar historial. Yo le daría la observación actual más un historial corto de acciones y precios, porque para jugar bien necesita detectar tendencias del mercado y recordar qué trabajadores ya han actuado durante el día.

La primera fase debería ser aprender legalidad y consecuencias, sin preocuparse todavía por ganar. Después comprobaríamos que sabe:

No dejar morir plantas ni animales.
Entender cuándo una cosecha está lista.
Comprar solo lo que puede pagar.
Diferenciar acciones de granjero y órdenes de mercado.
Interpretar correctamente el cambio de día.
Evitar perder productos por saturación del almacén.
Una vez domine eso, pasaríamos al aprendizaje competitivo. El dataset, por tanto, debe priorizar diversidad de estados y cobertura de reglas, no únicamente partidas ganadoras.


La unidad principal debería ser una observación por decisión, es decir, una transición:

(
𝑒
𝑠
𝑡
𝑎
𝑑
𝑜
𝑡
,
 
𝑎
𝑐
𝑐
𝑖
𝑜
ˊ
𝑛
𝑡
,
 
𝑟
𝑒
𝑐
𝑜
𝑚
𝑝
𝑒
𝑛
𝑠
𝑎
𝑡
,
 
𝑒
𝑠
𝑡
𝑎
𝑑
𝑜
𝑡
+
1
,
 
𝑡
𝑒
𝑟
𝑚
𝑖
𝑛
𝑎
𝑑
𝑜
)
(estado 
t
​
 , acci 
o
ˊ
 n 
t
​
 , recompensa 
t
​
 , estado 
t+1
​
 , terminado)

No sería una sola observación por partida. Una partida tiene muchas observaciones, porque el agente toma decisiones durante 720 turnos.

Ejemplo:


Como cada turno puede tener acciones del granjero, trabajadores y mercado, la acción completa sería algo parecido a:


Aunque internamente existan varias acciones, para el agente ese conjunto es la decisión de un turno. Por eso la muestra sería:


La partida completa sería una trayectoria:


Y además guardaríamos metadatos de la partida:


Hay que distinguir dos conceptos:

Observación: el estado visible antes de actuar.
Muestra de entrenamiento: observación más acción y consecuencia.
Para aprender las reglas, usamos principalmente:


Así aprende qué provoca cada acción.

Para aprender a ganar, añadimos la recompensa:


La recompensa puede ser pequeña durante la partida, por ejemplo dinero ganado o una planta perdida, y una recompensa final fuerte según el dinero bancario y el resultado contra el oponente.

Importante: no debemos guardar solo las acciones exitosas. También hay que guardar:

Acciones inválidas.
Acciones que no hacen nada.
Acciones demasiado tardías.
Acciones que provocan pérdidas.
Acciones que consumen turnos sin beneficio.
Esas transiciones enseñan las reglas y sus consecuencias.

En resumen: una partida contiene muchas observaciones; cada turno produce una muestra (estado, acción, resultado, siguiente estado). La partida completa sirve como contexto estratégico, mientras que cada transición sirve para aprender la relación entre decisión y consecuencia




. Antes de escribir código, definamos el contrato de nuestras funciones:

observación bruta
        ↓
funciones de extracción y feature engineering
        ↓
diccionario de features
        ↓
vector numérico para el modelo

Yo separaría claramente:

Features brutas: valores que ya existen en obs.

Features sintéticas: valores calculados a partir de uno o más datos brutos.

Datos descartados o reservados: información que existe, pero que no usaremos todavía.

La primera versión debe ser suficientemente completa, pero no exageradamente compleja.

1. Estructura general de las features

Propongo estas categorías:

### Features

│
├── A. Tiempo
├── B. Economía propia
├── C. Inventario propio
├── D. Semillas propias
├── E. Estado de mi granja
├── F. Producción propia
├── G. Obligaciones y riesgos
├── H. Mercado
├── I. Town / demanda
├── J. Oponente
├── K. Posición y operaciones
└── L. Features derivadas globales
## A. Features brutas de tiempo


Fuente:

obs["step"]
obs["day"]
obs["hour"]
### Features utilizadas directamente


Feature

	

Fuente

	

Tipo




step

	

obs["step"]

	

Bruta




day

	

obs["day"]

	

Bruta




hour

	

obs["hour"]

	

Bruta

### Features generadas


Feature

	

Datos necesarios

	

Significado




days_remaining

	

day

	

Días que faltan para terminar




steps_remaining

	

step

	

Steps restantes




season_progress

	

step

	

Progreso normalizado de la partida




is_last_day

	

day

	

Si estamos en el último día




is_last_week

	

day

	

Si quedan pocos días




is_day_start

	

hour

	

Si estamos al comienzo del día




is_day_end

	

hour

	

Si estamos cerca del final del día

Usaremos:

total_steps = 720
total_days = 30
hours_per_day = 24

Por ejemplo:

days_remaining = 30 - day
steps_remaining = 720 - step
season_progress = step / 720
Decisión

step, day y hour son redundantes parcialmente, pero al principio los conservamos. Más adelante podemos eliminar los que no aporten.

## B. Economía propia


Fuente:

my_farm = obs["farms"][obs["player"]]
my_farm["money"]
Feature bruta

Feature

	

Fuente




money

	

my_farm["money"]

### Features sintéticas


Feature

	

Datos necesarios

	

Significado




money_normalized

	

money

	

Dinero escalado




land_value

	

unlocked_quadrants

	

Valor aproximado de la tierra desbloqueada




animal_asset_value

	

animales presentes

	

Valor de compra de los animales




inventory_value

	

inventario + precios de mercado

	

Valor potencial del inventario




seed_value

	

semillas + precios/costos

	

Valor de las semillas




patrimonio

	

dinero + tierra + animales + inventario + semillas

	

Riqueza estimada total




liquidity_ratio

	

dinero / patrimonio

	

Porcentaje de patrimonio disponible en efectivo




money_per_day_remaining

	

dinero + days_remaining

	

Liquidez disponible por día




can_afford_land

	

dinero + costo próxima tierra

	

Capacidad de expansión




can_afford_animal

	

dinero + precio animal

	

Capacidad de comprar un animal




can_afford_seed

	

dinero + precio semilla

	

Capacidad de comprar semillas

Importante sobre patrimonio

No debemos usar solamente:

patrimonio

También conservamos sus componentes:

money
inventory_value
animal_asset_value
land_value
seed_value

Porque estos dos estados podrían tener el mismo patrimonio:

Estado A:
money = 3000
animales = 0

Estado B:
money = 100
animales = 2900

Pero son situaciones muy diferentes desde el punto de vista de liquidez.

## C. Inventario propio


Fuente:

obs["private"]["shed"]

En la observación tenemos:

WHEAT
CARROT
TOMATO
STRAWBERRY
MELON
EGG
MILK
WOOL
FERTILIZER
GOOSE
COW
SHEEP
### Features brutas


Para cada elemento:

shed_WHEAT
shed_CARROT
shed_TOMATO
shed_STRAWBERRY
shed_MELON
shed_EGG
shed_MILK
shed_WOOL
shed_FERTILIZER
shed_GOOSE
shed_COW
shed_SHEEP

En este caso, por ejemplo:

shed_WHEAT = obs["private"]["shed"]["WHEAT"]
### Features sintéticas


Feature

	

Datos necesarios

	

Significado




inventory_total_units

	

todos los productos del shed

	

Cantidad total de objetos




inventory_product_units

	

productos, excluyendo animales

	

Productos almacenados




inventory_animal_units

	

GOOSE, COW, SHEEP

	

Animales en inventario




inventory_value

	

cantidades + precios de mercado

	

Valor económico potencial




inventory_space_used

	

cantidades del shed

	

Espacio ocupado




inventory_space_free

	

capacidad shed − ocupado

	

Espacio restante




inventory_full_ratio

	

espacio usado / capacidad

	

Porcentaje de ocupación




wheat_reserve_value

	

shed_WHEAT + precio wheat

	

Valor de la reserva de trigo




fertilizer_stock

	

shed_FERTILIZER

	

Fertilizante disponible




has_sellable_products

	

productos del shed

	

Si existe algo vendible




has_feed_reserve

	

wheat disponible

	

Si tenemos alimento almacenado

Capacidad del shed

Según la especificación:

shed_capacity = 100

Pero cuidado: las semillas no se guardan en el shed y no deben contar para su capacidad.

## D. Semillas propias


Fuente:

obs["private"]["seeds"]
### Features brutas

seed_WHEAT
seed_CARROT
seed_TOMATO
seed_STRAWBERRY
seed_MELON
### Features sintéticas


Feature

	

Datos necesarios




total_seeds

	

todas las semillas




seed_inventory_value

	

semillas + costo/precio de compra




has_wheat_seed

	

seed_WHEAT




has_high_value_seed

	

melon/strawberry/tomato




cheapest_available_seed

	

cantidades + costos




seed_diversity

	

cantidad de tipos de semillas disponibles

No usaría todavía:

seed_profit_expected

porque requiere un modelo más complejo que considere tiempo, agua, fertilizante, precio futuro y espacio.

## E. Estado de mi granja


Fuente:

my_farm["tiles"]

La matriz contiene:

None
"LOCKED"
WEED
PLANT
COOP
PASTURE

Aquí no conviene copiar literalmente los 100 tiles al principio. Vamos a recorrerlos y generar un resumen.

### Features sintéticas generales


Feature

	

Datos necesarios




total_tiles

	

dimensiones de tiles




locked_tiles

	

tiles con "LOCKED"




unlocked_tiles

	

total − locked




empty_tiles

	

tiles None




weed_tiles

	

tiles con kind == "WEED"




plant_tiles

	

tiles con kind == "PLANT"




animal_structure_tiles

	

COOP + PASTURE




occupied_tiles

	

weeds + plants + structures




free_unlocked_tiles

	

empty unlocked tiles




farm_occupancy_ratio

	

occupied / unlocked




weed_ratio

	

weeds / unlocked




productive_tiles

	

plants + structures with animals




unlocked_quadrant_count

	

cantidad de cuadrantes desbloqueados

### Features brutas o casi brutas de expansión


Feature

	

Fuente




unlocked_NW

	

"NW" in unlocked_quadrants




unlocked_NE

	

"NE" in unlocked_quadrants




unlocked_SW

	

"SW" in unlocked_quadrants




unlocked_SE

	

"SE" in unlocked_quadrants

Estas son features binarias generadas desde:

my_farm["unlocked_quadrants"]
## F. Plantas


Fuente:

tile

cuando:

tile["kind"] == "PLANT"

Los cultivos posibles son:

WHEAT
CARROT
TOMATO
STRAWBERRY
MELON
### Features sintéticas por tipo de cultivo


Para cada cultivo, por ejemplo WHEAT:

Feature

	

Datos necesarios




wheat_count

	

cantidad de plantas wheat




wheat_total_yield_units

	

suma de yield_units




wheat_average_yield_units

	

yield total / cantidad




wheat_watered_count

	

watered_today




wheat_unwatered_count

	

no watered today




wheat_at_risk_count

	

consecutive_unwatered alto




wheat_fertilized_count

	

fertilized_until_day válido




wheat_average_age

	

day - planted_day




wheat_oldest_age

	

edad máxima




wheat_ready_count

	

cultivo listo para cosechar




wheat_expiring_count

	

próximo a caducar




wheat_expected_units

	

yield esperado según estado




wheat_expected_value

	

unidades esperadas × precio actual

Repetimos para:

carrot
tomato
strawberry
melon
### Features generales de plantas


Feature

	

Datos necesarios




total_plants

	

todas las plantas




total_yield_units

	

suma de yield_units




total_watered_plants

	

watered_today




total_unwatered_plants

	

plantas no regadas




plants_at_risk

	

consecutive_unwatered




fertilized_plants

	

fertilized_until_day




plants_ready_now

	

reglas de maduración




plants_expiring_soon

	

max_lifespan_step




plant_value

	

producción estimada × precios




average_plant_age

	

day - planted_day




young_plants

	

edad baja




old_plants

	

edad alta

## G. Features relacionadas con la producción


Estas son muy importantes porque conectan la granja con la economía.

Producción inmediata

Feature

	

Datos necesarios




production_ready_now

	

plantas/animales listos para producir




harvestable_units_now

	

yield_units + reglas del cultivo




harvestable_value_now

	

unidades + precios actuales




production_value_next_24h

	

estado de plantas + calendario de producción




production_value_next_48h

	

estado de plantas + calendario




production_value_remaining

	

plantas + días restantes




production_units_remaining

	

cultivos + reglas de producción




productive_tiles

	

plantas + animales activos

Producción por producto
expected_WHEAT_next_24h
expected_CARROT_next_24h
expected_TOMATO_next_24h
expected_STRAWBERRY_next_24h
expected_MELON_next_24h
expected_EGG_next_24h
expected_MILK_next_24h
expected_WOOL_next_24h

Y también:

expected_WHEAT_value_next_24h
expected_MILK_value_next_24h
...
Advertencia

Estas features no son simplemente datos brutos. Necesitan conocer:

crop
planted_day
yield_units
watered_today
fertilized_until_day
max_lifespan_step
day
hour

y las reglas de producción del juego.

Por eso probablemente las implementaremos en una función separada:

calculate_production_features(...)
## H. Animales y estructuras


Fuente:

tile["kind"] == "COOP"
tile["kind"] == "PASTURE"
### Features por animal


Para cada tipo:

GOOSE
COW
SHEEP

Feature

	

Datos necesarios




goose_count

	

estructuras con animal == "GOOSE"




cow_count

	

estructuras con animal == "COW"




sheep_count

	

estructuras con animal == "SHEEP"




goose_fed_count

	

fed_today




cow_fed_count

	

fed_today




sheep_fed_count

	

fed_today




animals_at_risk

	

consecutive_unfed




animals_cared_count

	

cared_today




pending_care_bonus_total

	

pending_care_bonus




fertilizer_available_count

	

fertilizer_available




animal_production_ready

	

calendario de producción




animal_production_value

	

producción × precio

### Features generales


Feature

	

Datos necesarios




total_animals

	

goose + cow + sheep




total_coops

	

estructuras COOP




total_pastures

	

estructuras PASTURE




empty_animal_structures

	

estructuras sin animal




animals_fed_today

	

fed_today




animals_unfed_today

	

no fed




animals_at_risk

	

consecutive_unfed




animal_asset_value

	

animales × costo de compra




animal_production_value

	

producción esperada




fertilizer_available_total

	

fertilizante disponible




pending_care_bonus_total

	

suma de bonuses

## I. Obligaciones y riesgos


Estas features se calculan sobre plantas y animales.

Alimentación

Feature

	

Datos necesarios




wheat_required_today

	

cantidad de animales




wheat_required_next_2_days

	

cantidad de animales




wheat_required_remaining

	

animales + días restantes




wheat_survival_days

	

wheat disponible / consumo diario




has_enough_wheat_today

	

wheat disponible + necesidad




has_enough_wheat_next_2_days

	

wheat disponible + necesidad

Riesgo de plantas

Feature

	

Datos necesarios




plants_at_risk

	

consecutive_unwatered




plants_unwatered_today

	

watered_today




plants_that_will_become_weeds

	

reglas de dos días sin agua




watering_work_remaining

	

plantas que necesitan agua




fertilizer_expiring_soon

	

fertilized_until_day

Riesgo de animales

Feature

	

Datos necesarios




animals_at_risk

	

consecutive_unfed




animals_unfed_today

	

fed_today




animals_that_may_escape

	

reglas de alimentación




feeding_work_remaining

	

animales no alimentados




care_work_remaining

	

animales no cuidados

Estas features pueden ayudar al agente a aprender que gastar todo el dinero puede ser peligroso si después no puede mantener la granja.

## J. Mercado


Fuente:

obs["market"]["inventory"]
obs["market"]["prices"]

Productos:

WHEAT
CARROT
TOMATO
STRAWBERRY
MELON
EGG
MILK
WOOL
FERTILIZER
### Features brutas


Para cada producto:

market_inventory_WHEAT
market_price_WHEAT
market_inventory_CARROT
market_price_CARROT
...
### Features sintéticas por producto


Feature

	

Datos necesarios




market_delta_WHEAT

	

inventario − I0




market_scarcity_WHEAT

	

si inventario < I0




market_glut_WHEAT

	

si inventario > I0




price_ratio_WHEAT

	

precio actual / precio base




price_difference_WHEAT

	

precio actual − precio base




price_premium_WHEAT

	

diferencia relativa respecto al base




market_inventory_ratio_WHEAT

	

inventario / I0




is_expensive_WHEAT

	

precio actual alto




is_cheap_WHEAT

	

precio actual bajo

Repetimos para todos los productos.

### Features generales del mercado


Feature

	

Datos necesarios




market_total_inventory

	

inventarios de productos




market_scarce_products

	

productos debajo de I0




market_glut_products

	

productos encima de I0




most_expensive_product

	

precios




cheapest_product

	

precios




average_price_ratio

	

ratios de precios




market_volatility_proxy

	

requeriría precios anteriores

Importante

No podemos calcular todavía una verdadera:

price_change
price_trend
price_volatility

porque la observación actual solamente contiene el estado presente.

Para eso necesitaremos guardar un historial:

market_price_history

durante la partida.

## K. Town y demanda


Fuente:

obs["town"]["unlocked_shops"]

Ejemplo:

[
    "PIZZA_SHOP",
    "SMOOTHIE_SHOP",
    "FARMERS_MARKET",
    ...
]

No metemos los strings directamente en el vector.

### Features sintéticas de cantidad de shops

bakery_count
pizza_shop_count
brunch_spot_count
yarn_store_count
ice_cream_shop_count
pet_cafe_count
smoothie_shop_count
farmers_market_count
### Features de demanda


A partir de los shops:

demand_WHEAT
demand_CARROT
demand_TOMATO
demand_STRAWBERRY
demand_EGG
demand_MILK
demand_WOOL

Por ejemplo:

PIZZA_SHOP:
    MILK
    TOMATO
    WHEAT

Entonces un Pizza Shop suma demanda a esos productos.

### Features adicionales


Feature

	

Datos necesarios




total_unlocked_shops

	

longitud de shops




unique_shop_types

	

tipos diferentes




most_demanded_product

	

demanda calculada




demand_WHEAT_normalized

	

demanda / cantidad shops




demand_pressure_WHEAT

	

demanda + inventario del mercado




demand_pressure_ratio_WHEAT

	

demanda / market inventory

Advertencia

La demanda que calculamos aquí es una estimación estructural, no necesariamente el consumo exacto del próximo turno, porque los shops consumen según sus propios intervalos temporales.

Más adelante podemos agregar:

shop_consumption_due_soon

pero eso requiere conocer el momento exacto del ciclo de consumo.

## L. Oponente


Fuente:

opponent_farm = obs["farms"][1 - obs["player"]]

Del oponente tenemos menos información que de nosotros.

### Features brutas


Feature

	

Fuente

# Kaggriculture — Business Experts Brainstorming

## 1. Objective

The objective is to transform the raw Kaggriculture game observation (`obs`) into meaningful business-domain features that can later be used by decision-making and Machine Learning models.

The architecture is based on a set of specialized **Business Experts**.

Each Expert is responsible for one specific business domain.

The first layer is deliberately deterministic: it describes and interprets the current game state without making strategic decisions.

---

# 2. Architecture

```text
                              OBS
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
 FinancialExpert       AgricultureExpert      LivestockExpert
          │                    │                    │
          ▼                    ▼                    ▼
 InventoryExpert        MarketExpert        OperationsExpert
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                       ProductionExpert
                               │
                               ▼
                      Decision / ML Layer
```

## Architectural principles

* `obs` is the **source of truth**.
* Every feature has one logical owner.
* Every Expert has a clearly defined business responsibility.
* Experts may query other Experts when they need information from another domain.
* An Expert must not modify another Expert's internal state.
* Each Expert exposes its information through a public interface.
* `get_features()` exposes the complete public feature set.
* Individual `get_*()` methods expose specific values.
* Internal implementation details remain encapsulated inside each Expert.
* The deterministic Business Expert layer does not make strategic decisions.
* Predictive, optimization and ML logic belongs to later layers.

---

# 3. Business Experts

The architecture contains seven specialized Business Experts:

1. `FinancialExpert`
2. `AgricultureExpert`
3. `LivestockExpert`
4. `InventoryExpert`
5. `MarketExpert`
6. `OperationsExpert`
7. `ProductionExpert`

Current implementation status:

```text
┌──────────────────────┬──────────────┐
│ Expert               │ Status       │
├──────────────────────┼──────────────┤
│ FinancialExpert      │ DONE         │
│ AgricultureExpert    │ DONE         │
│ LivestockExpert      │ DONE         │
│ InventoryExpert      │ DONE         │
│ MarketExpert         │ PLANNED     │
│ OperationsExpert     │ PLANNED     │
│ ProductionExpert     │ PLANNED     │
└──────────────────────┴──────────────┘
```

---

# 4. FinancialExpert

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

It does not own the physical inventory state or detailed livestock state.

---

## 4.1 Autonomy

`FinancialExpert` is deliberately **completely autonomous**.

It obtains financial information directly from:

```text
obs
├── farms[player]
├── private
└── market
```

This avoids making financial state dependent on another Expert's interpretation.

---

## 4.2 Financial features

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

### Animal financial representation

* `animals`
* `current_animals`
* `animal_asset_value`

The animal state itself belongs to `LivestockExpert`.

`FinancialExpert` only needs the current animal population in order to calculate its economic value.

---

## 4.3 Animal asset valuation

Animals are financial assets.

Current acquisition values:

```text
GOOSE  = $300
COW    = $400
SHEEP  = $500
```

The financial value is therefore:

```text
animal_asset_value =
    GOOSE × 300
  + COW × 400
  + SHEEP × 500
```

Animals must be counted regardless of whether they are:

* placed on the farm
* stored in the shed
* carried by the farmer or a farm hand

The detailed livestock state remains the responsibility of `LivestockExpert`.

---

## 4.4 Land valuation

Land is valued using historical/acquisition cost.

The initial `NW` quadrant belongs to the initial farm and therefore has no additional acquisition cost.

Additional quadrants are acquired progressively:

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

`land_value` represents **historical/acquisition value**.

It does not represent:

* predicted resale value
* speculative market value
* future appreciation

---

## 4.5 Net worth

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
    cash
    + assets
```

Currently:

```text
balance = net_worth
```

---

## 4.6 Liquidity

```text
liquidity_ratio =
    cash / net_worth
```

This represents the proportion of the player's financial value immediately available as cash.

Planning indicator:

```text
money_per_day_remaining =
    cash / days_remaining
```

This is a planning indicator and not an accounting measure.

---

## 4.7 Transactions

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

Therefore the reduction in cash is not automatically a financial loss.

Transactions can be classified as:

* `BUY_SEED`
* `BUY_PRODUCT`
* `BUY_ANIMAL`
* `SELL`
* `HIRE`
* `BUY_LAND`
* `BUILD_COOP`
* `BUILD_PASTURE`

Asset acquisitions such as animals and land are distinguished from operating expenses.

---

## 4.8 Observation without action

The current financial state can be calculated from:

```python
financial.process_observation(obs)
```

including:

* cash
* assets
* inventory value
* seed value
* animal value
* land value
* net worth
* liquidity
* balance

However, `income` and `expenses` cannot always be reconstructed reliably from an isolated observation.

When no action is available, observed cash variation may be used:

```text
cash_flow =
    current_cash - previous_cash
```

The system does not invent an income/expense classification.

---

## 4.9 Investment return

`investment_return` currently represents an **aggregate financial result**.

It is deliberately **not individual ROI**.

The current deterministic layer does not calculate:

```text
ROI of one cow
ROI of one sheep
ROI of one goose
ROI of one pasture
ROI of one coop
ROI of one land quadrant
```

Individual attribution requires knowing exactly which asset generated which income.

This belongs to a future analytical layer.

---

## 4.10 Payback

Current payback is aggregate:

```text
payback =
    acquisition_cost / investment_return
```

when the return is positive.

It is not individual asset payback.

---

# 5. AgricultureExpert

## Status

**Implemented**

## Responsibility

`AgricultureExpert` owns the current agricultural state of the player's farm.

It describes crops, agricultural surface and current crop production state.

It does not make agricultural decisions.

---

## 5.1 Temporal state

* `step`
* `day`
* `hour`

---

## 5.2 Farm surface

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

## 5.3 Crop state

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

## 5.4 Crop aggregation

The Expert aggregates crop information by type.

Examples:

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

## 5.5 Production state

AgricultureExpert describes the production currently represented by crops.

It does not attempt to predict market prices or optimize crop selection.

Future production prediction belongs to later analytical layers and/or `ProductionExpert`.

---

# 6. LivestockExpert

## Status

**Implemented**

## Responsibility

`LivestockExpert` owns the current operational and productive state of livestock.

It answers:

> What animals currently exist, where are they, and what is their current state?

It does not make decisions.

It does not:

* buy animals
* sell animals
* feed animals
* care for animals
* decide where to place animals
* calculate financial profitability
* calculate ROI
* optimize livestock strategy

---

# 6.1 Source of truth

A critical finding from actual Kaggriculture observations is that placed animals are explicitly represented in the farm tile.

An occupied pasture can appear as:

```python
{
    'kind': 'PASTURE',
    'animal': 'COW',
    'placed_day': 10,
    'yield_units': 0,
    'consecutive_unfed': 1,
    'fed_today': False,
    'cared_today': False,
    'fertilizer_available': True,
    'pending_care_bonus': 0
}
```

Therefore:

```text
tile["animal"]
```

is the source of truth for an animal currently placed on a `COOP` or `PASTURE`.

No historical action tracker is required to reconstruct the current placed-animal state.

---

# 6.2 Animal locations

Animals can currently exist in three relevant states:

```text
                    ANIMAL
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     Placed          Shed          Carried
     on farm                       inventory
```

### Placed animals

Detected by scanning:

```text
me["tiles"]
```

and checking:

```python
tile["kind"] in ("COOP", "PASTURE")
tile["animal"]
```

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

# 6.3 Animal population

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

This exact situation has been confirmed in real observations.

---

# 6.4 Individual animal state

For placed animals, `LivestockExpert` exposes detailed information including:

* animal type
* location
* x
* y
* placed day
* age in days
* yield units
* consecutive unfed days
* fed today
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
    'placed_day': 10,
    'age_days': ...,
    'yield_units': 0,
    'consecutive_unfed': 1,
    'fed_today': False,
    'cared_today': False,
    'fertilizer_available': True,
    'pending_care_bonus': 0
}
```

---

# 6.5 Livestock features

Current public state includes:

### Population

* `animals`
* `placed_animals`
* `shed_animals`
* `carried_animals`
* `total_animals`

### Detailed animal state

* `animal_details`

The detailed representation allows future synthetic features to be derived without changing the fundamental responsibility of the Expert.

Potential future derived features include:

* number of unfed animals
* number of animals at feeding risk
* number of animals ready to produce
* total animal yield
* available fertilizer
* animal production capacity

These should only be added after the underlying game rules have been completely verified.

---

# 7. InventoryExpert

## Status

**Implemented**

## Responsibility

`InventoryExpert` owns the current **physical inventory state**.

It answers:

> What physical resources does the player currently have and where are they?

It does not calculate economic value.

It does not decide what to buy or sell.

---

# 7.1 Inventory domains

Inventory is divided into three distinct areas:

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

Seeds are a separate inventory category.

They are not part of shed capacity.

### Shed

Obtained from:

```python
private["shed"]
```

The shed contains physical stock such as:

* products
* fertilizer
* animals waiting to be placed

### Carried inventories

Obtained from:

```python
private["inventories"]
```

These represent items currently carried by the farmer and farm hands.

---

# 7.2 Shed capacity

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

# 7.3 Physical inventory features

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

`InventoryExpert` does not include animals placed on the farm.

Placed animals belong to `LivestockExpert`.

---

# 7.4 Architectural distinction

```text
InventoryExpert
    └── What do I physically have?

FinancialExpert
    └── What is it worth?

LivestockExpert
    └── What is the operational state of my animals?
```

---

# 8. MarketExpert

## Status

**Planned**

## Responsibility

`MarketExpert` analyzes the current market.

It owns market-related information rather than financial or production information.

---

## Planned features

* current prices
* product prices
* seed prices
* animal prices
* market availability
* price ratios
* scarcity
* glut
* market pressure

---

## Future historical features

These require observations across time:

* price trend
* price volatility
* price momentum
* price history
* future price prediction

Prediction is not part of the first deterministic layer.

---

# 9. OperationsExpert

## Status

**Planned**

## Responsibility

`OperationsExpert` represents operational capacity, movement and workforce utilization.

---

## Planned features

### Farmer

* farmer position
* farmer x
* farmer y

### Hands

* hands count
* hires today
* has hands
* hands per task

### Tasks

* tasks
* tasks remaining
* workload
* estimated actions needed

### Distances

* distance to shed
* nearest plant
* nearest animal
* nearest weed
* nearest empty tile

`distance_to_shed` remains pending final confirmation of the actual shed position representation.

---

# 10. ProductionExpert

## Status

**Planned**

## Responsibility

`ProductionExpert` is the integration layer for production.

It does not replace AgricultureExpert or LivestockExpert.

Its purpose is to answer:

> How much can the farm produce now and in the near future?

---

## Planned features

* current production
* immediate production
* future production
* production in 24h
* production in 48h
* remaining production
* expected production
* expected production value
* crop production
* animal production

It may query:

```text
AgricultureExpert
LivestockExpert
MarketExpert
FinancialExpert
```

but does not duplicate their internal responsibilities.

---

# 11. Feature ownership

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
| `animal_production_state` | LivestockExpert   |
| `shed_stock`              | InventoryExpert   |
| `inventory_capacity`      | InventoryExpert   |
| `seed_stock`              | InventoryExpert   |
| `market_price`            | MarketExpert      |
| `price_trend`             | MarketExpert      |
| `farmer_position`         | OperationsExpert  |
| `hands_count`             | OperationsExpert  |
| `expected_production`     | ProductionExpert  |

An Expert may consume a feature owned by another Expert, but it does not become the owner of that feature.

---

# 12. Communication between Experts

The standard interface is:

```python
expert.process_observation(obs)
```

to update the Expert's internal state.

The complete public feature set is exposed through:

```python
expert.get_features()
```

Individual values are exposed through:

```python
expert.get_xxx()
```

---

# 13. Expert encapsulation

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

The relationship is therefore:

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

# 14. Deterministic Business Layer

The current Business Experts are intentionally deterministic.

Their responsibility is:

```text
RAW OBSERVATION
       │
       ▼
Business Experts
       │
       ▼
Structured domain state
       │
       ▼
Synthetic Features
```

The Experts should first represent the game correctly before introducing predictive models.

This separation makes it possible to verify each domain independently.

---

# 15. Features intentionally postponed

The following features are deliberately excluded from the first deterministic layer because they require historical data, simulation, attribution, optimization or predictive models.

## Market prediction

```text
price_trend
price_volatility
future_price_prediction
```

## Optimization

```text
exact_profit_per_crop
optimal_crop
optimal_action
opportunity_cost
```

## Asset attribution

```text
ROI of individual animal
ROI of individual crop
ROI of individual structure
ROI of individual land quadrant
individual asset payback
```

These require an attribution model capable of connecting costs and revenues to specific assets.

## Opponent prediction

```text
opponent_real_patrimony
opponent_future_strategy
```

These belong to later analytical/ML layers.

---

# 16. Long-term architecture

The Business Experts form the deterministic domain layer.

```text
                    RAW OBSERVATION

                           │
                           ▼

              ┌──────────────────────┐
              │   Business Experts   │
              │                      │
              │ Financial            │
              │ Agriculture          │
              │ Livestock            │
              │ Inventory            │
              │ Market               │
              │ Operations           │
              │ Production           │
              └──────────┬───────────┘
                         │
                         ▼

                  Synthetic Features

                         │
                         ▼

                  Decision / ML Layer

                         │
                         ▼

                       ACTION
```

The objective is **not** to create one giant model that learns everything directly from `obs`.

Instead:

1. Raw game data is interpreted by specialized domain Experts.
2. Each Expert owns a clearly defined business domain.
3. Experts generate deterministic, meaningful state representations.
4. Synthetic features are derived from those representations.
5. ML models can later learn decisions from the structured representation.
6. Predictive and optimization layers are added only where deterministic business logic is insufficient.

---

# 17. Current implementation roadmap

The current state is:

```text
FinancialExpert
      │
      └── DONE

AgricultureExpert
      │
      └── DONE

InventoryExpert
      │
      └── DONE

LivestockExpert
      │
      └── DONE

MarketExpert
      │
      └── NEXT

OperationsExpert
      │
      └── PLANNED

ProductionExpert
      │
      └── PLANNED
```

The next implementation step is therefore:

```text
MarketExpert
```

After the deterministic domain Experts are complete, the next phase will be the construction of **synthetic cross-domain features** and validation of the complete Business Expert layer before moving to the Decision / ML layer.
