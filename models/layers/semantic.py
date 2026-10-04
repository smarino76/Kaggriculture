from copy import deepcopy


class SemanticState:

    def __init__(
        self,
        financial_expert,
        agriculture_expert,
        inventory_expert,
        livestock_expert,
        market_expert,
        opponent_expert,
    ):
        self.financial = financial_expert
        self.agriculture = agriculture_expert
        self.inventory = inventory_expert
        self.livestock = livestock_expert
        self.market = market_expert
        self.opponent = opponent_expert

        self.semantic = {}

    def _get_market_context(self, product):
        price = self.market.get_price(product)
        return {
            "market_available": price is not None,
            "price": price,
            "price_change_pct": self.market.get_price_change_pct(product),
            "price_trend": self.market.get_price_trend(product),
            "market_pressure": self.market.get_market_pressure(product),
            "equilibrium_position": self.market.get_equilibrium_position(
                product
            ),
        }

    def process(self):
        """
        Construye la representación semántica del estado actual.

        SemanticState:
        - combina hechos producidos por los Business Experts;
        - identifica situaciones, riesgos, oportunidades y relaciones;
        - incorpora información observable del oponente;
        - puede construir relaciones entre nuestro estado y el del rival;
        - no decide acciones;
        - no utiliza ML;
        - no debe introducir target leakage.
        """

        self.semantic = {
            "risks": {},
            "opportunities": {},
            "situations": {},
            "relationships": {},
        }

        # Livestock presence is directly observable. Keep counts by location
        # to make the boolean result interpretable.
        total_animals = self.livestock.get_total_animals()
        placed_animals = self.livestock.get_placed_animals()
        shed_animals = self.livestock.get_shed_animals()
        carried_animals = self.livestock.get_carried_animals()

        self.semantic["situations"]["livestock_present"] = {
            "value": total_animals > 0,
            "details": {
                "total_animals": total_animals,
                "placed_animals": placed_animals,
                "shed_animals": shed_animals,
                "carried_animals": carried_animals,
            },
        }

        # Production is ready when at least one crop has positive yield,
        # matching AgricultureExpert's per-crop readiness rule.
        crop_details = self.agriculture.get_crop_details()
        ready_yield_by_product = {}
        ready_plants_by_product = {}
        for crop in crop_details:
            if crop.get("is_ready"):
                product = crop["crop"]
                ready_yield_by_product[product] = (
                    ready_yield_by_product.get(product, 0)
                    + crop.get("yield_units", 0)
                )
                ready_plants_by_product[product] = (
                    ready_plants_by_product.get(product, 0) + 1
                )

        production_ready_now = sum(ready_yield_by_product.values())
        self.semantic["situations"]["production_ready"] = {
            "value": production_ready_now > 0,
            "details": {
                "ready_plants": sum(ready_plants_by_product.values()),
                "production_ready_now": production_ready_now,
                "by_product": {
                    product: {
                        "ready_plants": ready_plants_by_product[product],
                        "yield_units": yield_units,
                    }
                    for product, yield_units in ready_yield_by_product.items()
                },
            },
        }

        # Needs-feed is an explicit observable maintenance condition from
        # LivestockExpert, so preserve both the flag and animal-level evidence.
        animals_needing_feed = [
            animal
            for animal in self.livestock.get_animal_details()
            if animal.get("needs_feed")
        ]
        self.semantic["situations"]["livestock_attention"] = {
            "value": bool(animals_needing_feed),
            "details": {
                "animals_needing_feed": len(animals_needing_feed),
                "animals": animals_needing_feed,
            },
        }

        shed_capacity = self.inventory.get_shed_capacity()
        shed_used = self.inventory.get_shed_used()
        shed_available = self.inventory.get_shed_available()
        shed_utilization = self.inventory.get_shed_utilization()
        self.semantic["situations"]["storage_state"] = {
            "value": shed_utilization,
            "details": {
                "shed_used": shed_used,
                "shed_capacity": shed_capacity,
                "shed_available": shed_available,
            },
        }

        cash = self.financial.get_cash()
        liquidity_ratio = self.financial.get_liquidity_ratio()
        net_worth = self.financial.get_net_worth()
        days_remaining = self.financial.get_days_remaining()
        steps_remaining = self.financial.get_steps_remaining()
        self.semantic["situations"]["liquidity_state"] = {
            "value": liquidity_ratio,
            "details": {
                "cash": cash,
                "net_worth": net_worth,
                "days_remaining": days_remaining,
                "steps_remaining": steps_remaining,
                "money_per_day_remaining": (
                    self.financial.get_money_per_day_remaining()
                ),
            },
        }

        season_progress = self.financial.get_season_progress()
        self.semantic["situations"]["time_pressure"] = {
            "value": season_progress,
            "details": {
                "season_progress": season_progress,
                "days_remaining": days_remaining,
                "steps_remaining": steps_remaining,
            },
        }

        market_prices = self.market.get_features().get("prices", {})
        market_by_product = {
            product: self._get_market_context(product)
            for product in market_prices
        }
        self.semantic["situations"]["market_state"] = {
            "value": bool(market_by_product),
            "details": {
                "products_with_market_data": len(market_by_product),
                "by_product": market_by_product,
            },
        }

        animals_at_escape_risk = [
            animal
            for animal in self.livestock.get_animal_details()
            if (
                animal.get("consecutive_unfed", 0) >= 1
                and not animal.get("fed_today", False)
            )
        ]
        self.semantic["risks"]["livestock_maintenance_risk"] = {
            "value": bool(animals_at_escape_risk),
            "details": {
                "animals_at_escape_risk": len(animals_at_escape_risk),
                "escape_rule_consecutive_unfed_days": 2,
                "animals": animals_at_escape_risk,
            },
        }

        physical_inventory = self.inventory.get_total_physical()
        inventory_market_by_product = {
            product: {
                "inventory_quantity": quantity,
                **self._get_market_context(product),
            }
            for product, quantity in physical_inventory.items()
            if quantity > 0
        }
        self.semantic["relationships"]["inventory_market_relationship"] = {
            "value": bool(inventory_market_by_product),
            "details": {
                "products_with_inventory": len(inventory_market_by_product),
                "by_product": inventory_market_by_product,
            },
        }

        production_market_by_product = {
            product: {
                "ready_plants": ready_plants_by_product[product],
                "yield_units": yield_units,
                **self._get_market_context(product),
            }
            for product, yield_units in ready_yield_by_product.items()
        }
        self.semantic["relationships"]["production_market_relationship"] = {
            "value": bool(production_market_by_product),
            "details": {
                "products_with_ready_production": len(
                    production_market_by_product
                ),
                "by_product": production_market_by_product,
            },
        }

        agricultural_surface = self.agriculture.get_agricultural_surface()
        crop_surface = (
            self.agriculture.get_occupied_agricultural_surface()
        )
        weed_surface = (
            self.agriculture.get_weed_agricultural_surface()
        )
        occupied_surface = crop_surface + weed_surface
        free_surface = self.agriculture.get_free_agricultural_surface()
        occupied_surface_ratio = (
            occupied_surface / agricultural_surface
            if agricultural_surface > 0
            else 0.0
        )
        self.semantic["situations"]["farm_capacity_state"] = {
            "value": occupied_surface_ratio,
            "details": {
                "agricultural_surface": agricultural_surface,
                "occupied_surface": occupied_surface,
                "crop_surface": crop_surface,
                "weed_surface": weed_surface,
                "free_surface": free_surface,
            },
        }

        production_storage_gap = production_ready_now - shed_available
        self.semantic["relationships"]["production_storage_relationship"] = {
            "value": production_storage_gap,
            "details": {
                "production_ready_now": production_ready_now,
                "shed_available": shed_available,
                "shed_used": shed_used,
                "shed_capacity": shed_capacity,
                "capacity_gap_units": production_storage_gap,
            },
        }

        self.semantic["risks"]["storage_pressure"] = {
            "value": shed_available == 0,
            "details": {
                "shed_utilization": self.inventory.get_shed_utilization(),
                "shed_available": shed_available,
                "shed_capacity": shed_capacity,
                "shed_used": shed_used,
            },
        }

        self.semantic["risks"]["production_storage_risk"] = {
            "value": production_storage_gap > 0,
            "details": {
                "production_storage_relationship": deepcopy(
                    self.semantic["relationships"][
                        "production_storage_relationship"
                    ]
                ),
                "production_exceeding_available_storage": max(
                    0, production_storage_gap
                ),
            },
        }


    def get_features(self):
        return deepcopy(self.semantic)
