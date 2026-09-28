from experts.business import (
    FinancialExpert,
    AgricultureExpert,
    InventoryExpert,
    MarketExpert,
    LivestockExpert,
)
from pathlib import Path
from models.layers.semantic import SemanticState


market_expert = MarketExpert()

DEBUG_LOG_PATH = Path(__file__).with_name("agent_debug.log")

# Used only to avoid printing the same observation multiple times.
last_debug_step = None


def agent(obs):

    global last_debug_step

    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]

    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    # ---------------------------------------------------------
    # BUSINESS EXPERTS
    # ---------------------------------------------------------

    financial_expert = FinancialExpert(player=player)
    agriculture_expert = AgricultureExpert(player=player)
    inventory_expert = InventoryExpert(player=player)
    livestock_expert = LivestockExpert(player=player)

    semantic = SemanticState(livestock_expert=livestock_expert, market_expert=market_expert, inventory_expert=inventory_expert, financial_expert=financial_expert, agriculture_expert=agriculture_expert)
    
    
    financial_expert.process_observation(obs)
    agriculture_expert.process_observation(obs)
    inventory_expert.process_observation(obs)
    market_expert.process_observation(obs)
    livestock_expert.process_observation(obs)
    semantic.process()
    
    with open("semantic.log","w") as f:
        f.write(f"Semantic: {semantic.get_features()}\n")
    
    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    if (
        obs["step"] in range(330, 340)
        and obs["step"] != last_debug_step
    ):

        debug_output = (
            f"STEP: {obs['step']}\n"
            f"DAY: {obs['day']}\n"
            f"MONEY: {me['money']}\n"
            f"SHED: {private.get('shed')}\n"
            f"INVENTORIES: {private.get('inventories')}\n"
        )

        print(debug_output, flush=True)

        with DEBUG_LOG_PATH.open(
            "a",
            encoding="utf-8"
        ) as log_file:
            log_file.write(debug_output + "\n")

        # Print animals currently placed on the farm.
        for y, row in enumerate(me["tiles"]):

            for x, tile_data in enumerate(row):

                if (
                    isinstance(tile_data, dict)
                    and tile_data.get("animal")
                ):

                    animal_output = (
                        f"ANIMAL: {tile_data.get('animal')}\n"
                        f"POS: {(x, y)}\n"
                        f"TILE: {tile_data}\n"
                    )

                    print(animal_output, flush=True)

                    with DEBUG_LOG_PATH.open(
                        "a",
                        encoding="utf-8"
                    ) as log_file:
                        log_file.write(animal_output + "\n")

        # Print the state calculated by LivestockExpert.
        livestock_output = (
            f"LIVESTOCK EXPERT:\n"
            f"{livestock_expert.get_features()}\n"
        )

        print(livestock_output, flush=True)

        with DEBUG_LOG_PATH.open(
            "a",
            encoding="utf-8"
        ) as log_file:
            log_file.write(livestock_output + "\n")

        # Remember that this STEP has already been printed.
        last_debug_step = obs["step"]

    # ---------------------------------------------------------
    # ACTION HELPER
    # ---------------------------------------------------------

    def finish_action(farmer_action, market_actions=None):

        return {
            "farmer": farmer_action,
            "hands": [],
            "market": (
                market_actions
                if market_actions is not None
                else []
            ),
        }

    # ---------------------------------------------------------
    # MARKET ACTIONS
    # ---------------------------------------------------------

    market = []

    # ---------------------------------------------------------
    # INVENTORY / SHED
    # ---------------------------------------------------------

    shed_cows = private["shed"].get("COW", 0)

    # private["inventories"] contains the inventories of the
    # farmer / farm hands.
    inventories = private.get("inventories", [])

    farmer_inventory = (
        inventories[0]
        if inventories
        else {}
    )

    cows_in_inventory = farmer_inventory.get("COW", 0)

    has_cow = (
        shed_cows > 0
        or cows_in_inventory > 0
    )

    is_pasture = (
        isinstance(tile, dict)
        and tile.get("kind") == "PASTURE"
    )

    # ---------------------------------------------------------
    # MARKET
    # ---------------------------------------------------------

    # Buy a cow if we have no cow available
    # and enough money.
    if (
        not has_cow
        and me["money"] >= 400
    ):
        market.append(
            ["BUY_ANIMAL", "COW", 1]
        )

    # Buy a wheat seed if we have none
    # and enough money.
    if (
        private["seeds"].get("WHEAT", 0) == 0
        and me["money"] >= 10
    ):
        market.append(
            ["BUY_SEED", "WHEAT", 1]
        )

    # Sell any wheat sitting in the shed.
    wheat_in_shed = private["shed"].get(
        "WHEAT",
        0
    )

    if wheat_in_shed > 0:
        market.append(
            ["SELL", "WHEAT", wheat_in_shed]
        )

    # ---------------------------------------------------------
    # COW MANAGEMENT
    # ---------------------------------------------------------

    # 1. We have a cow in the shed but not
    #    in the farmer inventory.
    #
    #    (4,4), (5,4), (4,5), (5,5)
    #    are adjacent to the shed.
    if (
        shed_cows > 0
        and cows_in_inventory == 0
    ):

        if (fx, fy) in [
            (4, 4),
            (5, 4),
            (4, 5),
            (5, 5),
        ]:

            return finish_action(
                ["PICKUP", "COW", 1],
                market,
            )

    # 2. We are standing on an empty tile
    #    and have a cow.
    #
    #    Build the pasture first.
    if (
        tile is None
        and cows_in_inventory > 0
    ):

        return finish_action(
            ["BUILD_PASTURE"],
            market,
        )

    # 3. We are standing on a pasture
    #    and have a cow in the farmer inventory.
    if (
        is_pasture
        and cows_in_inventory > 0
    ):

        return finish_action(
            ["PLACE", "COW"],
            market,
        )

    # ---------------------------------------------------------
    # WHEAT
    # ---------------------------------------------------------

    # Empty tile -> plant wheat.
    if (
        tile is None
        and private["seeds"].get("WHEAT", 0) > 0
    ):

        return finish_action(
            ["PLANT", "WHEAT"],
            market,
        )

    # Plant -> water or harvest.
    if (
        isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
    ):

        crop_age = (
            obs["day"]
            - tile["planted_day"]
        )

        if crop_age >= 2:

            return finish_action(
                ["HARVEST"],
                market,
            )

        if not tile["watered_today"]:

            return finish_action(
                ["WATER"],
                market,
            )

    # ---------------------------------------------------------
    # DEFAULT
    # ---------------------------------------------------------

    return finish_action(
        ["PASS"],
        market,
    )