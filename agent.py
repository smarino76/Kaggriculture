from experts.business import FinancialExpert, AgricultureExpert, InventoryExpert


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]

    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    financial_expert = FinancialExpert(player=player)
    agriculture_expert = AgricultureExpert(player=player)
    inventory_expert = InventoryExpert(player=player)


    financial_expert.process_observation(obs)
    agriculture_expert.process_observation(obs)
    inventory_expert.process_observation(obs)

    # print(f"Inventory: {inventory_expert.get_features()}")

    market = []

    # ---------------------------------------------------------
    # INVENTORY / SHED
    # ---------------------------------------------------------

    shed_cows = private["shed"].get("COW", 0)

    # private["inventories"] contains the inventories of the
    # farmer / farm hands.
    inventories = private.get("inventories", [])

    farmer_inventory = inventories[0] if inventories else {}

    cows_in_inventory = farmer_inventory.get("COW", 0)

    has_cow = shed_cows > 0 or cows_in_inventory > 0

    is_pasture = (
        isinstance(tile, dict)
        and tile.get("kind") == "PASTURE"
    )

    # ---------------------------------------------------------
    # MARKET
    # ---------------------------------------------------------

    # Buy a cow if we have no cow available and enough money.
    if not has_cow and me["money"] >= 400:
        market.append(["BUY_ANIMAL", "COW", 1])

    # Buy a wheat seed if we have none and enough money.
    if private["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])

    # Sell any wheat sitting in the shed.
    wheat_in_shed = private["shed"].get("WHEAT", 0)

    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    # ---------------------------------------------------------
    # COW MANAGEMENT
    # ---------------------------------------------------------

    # 1. We have a cow in the shed but not in the farmer
    #    inventory.
    #
    #    (4,4) is adjacent to the shed, so PICKUP can be
    #    performed from there.
    if shed_cows > 0 and cows_in_inventory == 0:

        # If we are adjacent to the shed, pick up one cow.
        if (fx, fy) in [(4, 4), (5, 4), (4, 5), (5, 5)]:
            print(f"observacion antes de return PICKUP COW: {obs}")
            
            return {
                "farmer": ["PICKUP", "COW", 1],
                "hands": [],
                "market": market
            }

    # 2. We are standing on an empty tile and have a cow.
    #    Build the pasture first.
    if tile is None and cows_in_inventory > 0:
        print(f"observacion antes de return BUILD_PASTURE: {obs}")
 
        return {            
            "farmer": ["BUILD_PASTURE"],
            "hands": [],
            "market": market
        }

    # 3. We are standing on a pasture and have a cow
    #    in the farmer inventory.
    if is_pasture and cows_in_inventory > 0:
        print(f"observacion antes de return PLACE COW: {obs}")
        return {
            "farmer": ["PLACE", "COW"],
            "hands": [],
            "market": market
        }

    # ---------------------------------------------------------
    # WHEAT
    # ---------------------------------------------------------

    # Empty tile -> plant wheat.
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {
            "farmer": ["PLANT", "WHEAT"],
            "hands": [],
            "market": market
        }

    # Plant -> water or harvest.
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":

        crop_age = obs["day"] - tile["planted_day"]

        if crop_age >= 2:
            return {
                "farmer": ["HARVEST"],
                "hands": [],
                "market": market
            }

        if not tile["watered_today"]:
            return {
                "farmer": ["WATER"],
                "hands": [],
                "market": market
            }

    # ---------------------------------------------------------
    # DEFAULT
    # ---------------------------------------------------------

    return {
        "farmer": ["PASS"],
        "hands": [],
        "market": market
    }