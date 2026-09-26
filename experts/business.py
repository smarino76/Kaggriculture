class FinancialExpert:

    """
    FinancialExpert
    ===============

    Business Expert responsible for representing the financial
    situation of one player.

    Architectural principle
    ------------------------
    FinancialExpert is completely autonomous.

    It reads financial information directly from the game
    observation (obs) and does NOT depend on any other Business
    Expert.

    Its purpose is to transform raw game-state information into
    financial and economic features that can later be used by
    decision-making and AI/ML models.

    Main responsibilities
    ----------------------
    - cash
    - income
    - expenses
    - cash flow
    - inventory valuation
    - seed valuation
    - animal asset valuation
    - land value
    - total assets
    - net worth
    - liquidity
    - balance
    - investments
    - acquisition cost
    - investment return
    - payback

    Important accounting distinction
    ---------------------------------
    A change in cash is NOT necessarily an income or an expense.

    Example:

        BUY_ANIMAL COW

    causes:

        cash              ↓
        animal asset      ↑

    Therefore, the cash movement alone cannot be interpreted as
    an economic loss.

    For this reason, income and expenses are classified from the
    explicit action whenever the action is available.

    If process_observation() is called without an action, the
    current financial state can still be calculated correctly,
    but the individual income/expense transaction cannot always
    be reconstructed reliably from obs alone.
    """

    # =========================================================
    # GAME FINANCIAL CONSTANTS
    # =========================================================

    # Acquisition cost of animals.
    #
    # These values represent the cost paid when purchasing the
    # animal. They are intentionally NOT taken from market prices.
    #
    # The animal itself is treated as a productive asset.
    ANIMAL_COSTS = {
        'GOOSE': 300,
        'COW': 400,
        'SHEEP': 500,
    }

    # Additional land acquisition costs.
    #
    # The initial NW quadrant belongs to the farm and therefore
    # has no additional acquisition cost.
    #
    # Additional quadrants are acquired progressively:
    #
    #   first additional quadrant  -> $1,000
    #   second additional quadrant -> $2,000
    #   third additional quadrant  -> $4,000
    #
    # Therefore:
    #
    #   NW                         -> $0
    #   NW + one quadrant          -> $1,000
    #   NW + two quadrants         -> $3,000
    #   NW + three quadrants       -> $7,000
    LAND_PRICES = [
        1000,
        2000,
        4000,
    ]

    ANIMAL_TYPES = (
        'GOOSE',
        'COW',
        'SHEEP',
    )

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self, player=0):

        self.player = player

        # -----------------------------------------------------
        # Temporal state
        # -----------------------------------------------------

        self.step = None
        self.day = None
        self.hour = None

        self.days_remaining = None
        self.steps_remaining = None
        self.season_progress = None

        self.is_last_day = False
        self.is_last_week = False
        self.is_day_start = False
        self.is_day_end = False

        # -----------------------------------------------------
        # Financial state
        # -----------------------------------------------------

        self.cash = 0

        self.income = 0
        self.expenses = 0
        self.cash_flow = 0

        # -----------------------------------------------------
        # Assets
        # -----------------------------------------------------

        # Shed contains privately stored items.
        #
        # FinancialExpert does NOT manage the inventory.
        # It only reads the shed to calculate its economic value.
        self.shed = {}
        self.inventory_value = 0

        # Seeds are read from the private player state only for
        # financial valuation.
        self.seeds = {}
        self.seed_value = 0

        # -----------------------------------------------------
        # Animals
        # -----------------------------------------------------

        # self.animals
        # ------------
        # Financial representation of the player's animals.
        #
        # self.current_animals
        # --------------------
        # Temporary state reconstructed from obs.
        #
        # These are intentionally two different concepts.
        #
        # current_animals is used to determine how many animals
        # actually exist at the current observation.
        #
        # animals is the financial representation derived from
        # that current state.
        self.animals = {}
        self.current_animals = {}

        self.animal_asset_value = 0

        # -----------------------------------------------------
        # Land
        # -----------------------------------------------------

        # Land is represented using its acquisition cost.
        #
        # This is deliberately called "land_value" in the public
        # financial feature set, but technically it represents
        # acquisition value / historical cost rather than a
        # simulated resale market value.
        self.land_value = 0

        # -----------------------------------------------------
        # Net worth
        # -----------------------------------------------------

        self.net_worth = 0
        self.liquidity_ratio = 0
        self.money_per_day_remaining = 0

        # -----------------------------------------------------
        # Balance
        # -----------------------------------------------------

        # There are currently no explicit liabilities/debts in
        # the financial model.
        #
        # Therefore:
        #
        #     balance = cash + assets
        #
        # and this is equal to net_worth.
        self.assets = 0
        self.balance = 0

        # -----------------------------------------------------
        # Investments
        # -----------------------------------------------------

        self.investments = {}

        # Total acquisition cost of investments detected by
        # FinancialExpert.
        self.acquisition_cost = 0

        # Current aggregate return attributed to the investment
        # subsystem.
        self.investment_return = 0

        # Estimated payback period.
        self.payback = None

        # -----------------------------------------------------
        # Market
        # -----------------------------------------------------

        self.market = {}
        self.prices = {}

        # -----------------------------------------------------
        # Historical state
        # -----------------------------------------------------

        # These variables store the previous observation so that
        # changes between consecutive observations can be
        # calculated.
        self.previous_cash = None
        self.previous_shed = None
        self.previous_seed_value = None
        self.previous_animal_asset_value = None
        self.previous_land_value = None
        self.previous_net_worth = None

        # -----------------------------------------------------
        # Last transaction
        # -----------------------------------------------------

        # Stores a normalized representation of the last
        # transaction processed by the expert.
        self.last_transaction = None

    # =========================================================
    # PROCESS OBSERVATION
    # =========================================================

    def process_observation(self, obs, action=None):

        """
        Process one game observation.

        Parameters
        ----------
        obs : dict
            Current game observation.

        action : optional
            Action responsible for producing the current state.

            When available, it is used to classify financial
            transactions such as:

                BUY_SEED
                BUY_PRODUCT
                BUY_ANIMAL
                SELL
                HIRE
                BUY_LAND
                BUILD_COOP
                BUILD_PASTURE

            If action is None, the current financial state is
            still calculated, but income and expenses cannot
            always be reconstructed reliably.

        Important
        ---------
        The observation is always the source of truth for the
        current financial state.

        Historical values are maintained internally only to
        calculate changes between observations.
        """

        # -----------------------------------------------------
        # Save previous state BEFORE replacing it with the
        # current observation.
        # -----------------------------------------------------

        previous_cash = self.cash
        previous_shed = self.shed.copy()

        previous_seed_value = self.seed_value
        previous_animal_asset_value = (
            self.animal_asset_value
        )
        previous_land_value = self.land_value
        previous_net_worth = self.net_worth

        # =====================================================
        # GENERAL INFORMATION
        # =====================================================

        self.step = obs['step']
        self.day = obs['day']
        self.hour = obs['hour']

        # =====================================================
        # DERIVED TIME FEATURES
        # =====================================================

        total_steps = 720
        total_days = 30
        hours_per_day = 24

        self.days_remaining = max(
            0,
            total_days - self.day
        )

        self.steps_remaining = max(
            0,
            total_steps - self.step
        )

        self.season_progress = (
            self.step / total_steps
        )

        self.is_last_day = (
            self.day == total_days - 1
        )

        self.is_last_week = (
            self.days_remaining <= 7
        )

        self.is_day_start = (
            self.hour == 0
        )

        self.is_day_end = (
            self.hour == hours_per_day - 1
        )

        # =====================================================
        # PLAYER STATE
        # =====================================================

        self.me = obs['farms'][self.player]
        self.private = obs['private']

        # Current cash is directly available in the farm state.
        self.cash = self.me['money']

        # =====================================================
        # SHED
        # =====================================================

        self.shed = self.private['shed']

        # =====================================================
        # SEEDS
        # =====================================================

        self.seeds = self.private['seeds']

        # =====================================================
        # MARKET
        # =====================================================

        self.market = obs['market']
        self.prices = self.market['prices']

        # =====================================================
        # INVENTORY VALUE
        # =====================================================

        """
        Value of privately stored products.

        Animals stored in the shed are excluded here because
        animals are treated separately as productive assets and
        are included in animal_asset_value.

        Product inventory is valued using the current market
        price available in obs.
        """

        self.inventory_value = sum(
            self.prices.get(product, 0) * quantity
            for product, quantity in self.shed.items()
            if product not in self.ANIMAL_TYPES
        )

        # =====================================================
        # SEED VALUE
        # =====================================================

        """
        Seeds are treated separately from commercial inventory.

        Their value is based on acquisition price rather than
        the market prices used for harvested/commercial products.

        This prevents seed valuation from being confused with
        the value of products that can be sold through SELL.
        """

        seed_prices = {
            'WHEAT': 10,
            'CARROT': 20,
            'TOMATO': 50,
            'STRAWBERRY': 100,
            'MELON': 80,
        }

        self.seed_value = sum(
            seed_prices.get(seed, 0) * quantity
            for seed, quantity in self.seeds.items()
        )

        # =====================================================
        # ANIMALS
        # =====================================================

        """
        Reconstruct the complete current animal population.

        Animals can exist in two locations:

        1. inside the private shed/inventory;
        2. placed on a COOP or PASTURE tile.

        current_animals is therefore calculated from both
        sources.

        It is a temporary calculation state.

        self.animals is then populated from current_animals and
        represents the financial expert's current animal state.
        """

        self.current_animals = {
            animal: 0
            for animal in self.ANIMAL_TYPES
        }

        # Animals still stored in the shed.

        for animal in self.ANIMAL_TYPES:

            self.current_animals[animal] += (
                self.shed.get(animal, 0)
            )

        # Animals placed on farm structures.

        for row in self.me['tiles']:

            for tile in row:

                if not isinstance(tile, dict):
                    continue

                if tile.get('kind') not in (
                    'COOP',
                    'PASTURE'
                ):
                    continue

                animal = tile.get('animal')

                if animal in self.current_animals:
                    self.current_animals[animal] += 1

        # Financial representation of current animals.

        self.animals = self.current_animals.copy()

        # =====================================================
        # ANIMAL ASSET VALUE
        # =====================================================

        """
        Animals are productive assets.

        Their financial value is therefore based on acquisition
        cost, not on the current market price of a product.

        Example:

            one COW -> $400 acquisition value

        This is intentionally different from inventory_value.
        """

        self.animal_asset_value = sum(
            self.ANIMAL_COSTS[animal] * quantity
            for animal, quantity
            in self.animals.items()
        )

        # =====================================================
        # LAND VALUE
        # =====================================================

        """
        Land valuation
        ---------------

        The initial NW quadrant is part of the initial farm and
        therefore has no additional acquisition cost.

        Additional quadrants are acquired progressively:

            1st additional quadrant -> $1,000
            2nd additional quadrant -> $2,000
            3rd additional quadrant -> $4,000

        Therefore:

            ["NW"]
                -> $0

            ["NW", "NE"]
                -> $1,000

            ["NW", "NE", "SW"]
                -> $3,000

            ["NW", "NE", "SW", "SE"]
                -> $7,000

        IMPORTANT
        ---------
        land_value represents acquisition cost / historical
        acquisition value.

        It is NOT a predicted resale price or market valuation
        of the land.

        The model deliberately avoids inventing a land resale
        market that is not provided by the game.
        """

        unlocked_quadrants = self.me.get(
            'unlocked_quadrants',
            ['NW']
        )

        # NW is the initial quadrant.
        # Only additional quadrants have an acquisition cost.

        extra_quadrants = max(
            0,
            len(unlocked_quadrants) - 1
        )

        self.land_value = sum(
            self.LAND_PRICES[:extra_quadrants]
        )

        # =====================================================
        # TOTAL ASSETS
        # =====================================================

        """
        Assets excluding cash.

        Cash is kept separate because it is also the main
        liquidity measure.
        """

        self.assets = (
            self.inventory_value
            + self.seed_value
            + self.animal_asset_value
            + self.land_value
        )

        # =====================================================
        # NET WORTH
        # =====================================================

        """
        Net worth / patrimonio.

        No liabilities are currently modeled.

            net_worth =
                cash
                + inventory
                + seeds
                + animals
                + land
        """

        self.net_worth = (
            self.cash
            + self.assets
        )

        # =====================================================
        # LIQUIDITY
        # =====================================================

        """
        Liquidity ratio.

            liquidity_ratio =
                cash / net_worth

        This represents the proportion of total estimated
        financial value that is immediately available as cash.
        """

        if self.net_worth > 0:

            self.liquidity_ratio = (
                self.cash / self.net_worth
            )

        else:

            self.liquidity_ratio = 0

        # =====================================================
        # MONEY PER DAY REMAINING
        # =====================================================

        """
        Average cash available per remaining game day.

        This is a planning indicator, not an accounting measure.

        It answers approximately:

            "If the current cash were distributed evenly over
             the remaining days, how much cash would be available
             per day?"
        """

        if self.days_remaining > 0:

            self.money_per_day_remaining = (
                self.cash
                / self.days_remaining
            )

        else:

            self.money_per_day_remaining = self.cash

        # =====================================================
        # BALANCE
        # =====================================================

        """
        Current balance.

        The game currently provides no explicit liability/debt
        structure for this financial model.

        Therefore:

            balance = cash + assets

        and consequently:

            balance == net_worth
        """

        self.balance = (
            self.cash
            + self.assets
        )

        # =====================================================
        # TRANSACTION PROCESSING
        # =====================================================

        """
        Income, expenses and investments are processed separately
        because a cash movement cannot automatically be classified
        as an income or expense.

        Example:

            BUY_ANIMAL

        means:

            cash decreases
            asset value increases

        Therefore the transaction must be interpreted from the
        action whenever the action is available.
        """

        self._process_transaction(
            action=action,
            previous_cash=previous_cash,
        )

        # =====================================================
        # HISTORICAL STATE
        # =====================================================

        self.previous_cash = previous_cash

        self.previous_shed = previous_shed

        self.previous_seed_value = (
            previous_seed_value
        )

        self.previous_animal_asset_value = (
            previous_animal_asset_value
        )

        self.previous_land_value = (
            previous_land_value
        )

        self.previous_net_worth = (
            previous_net_worth
        )

    # =========================================================
    # TRANSACTION PROCESSING
    # =========================================================

    def _process_transaction(
        self,
        action,
        previous_cash,
    ):

        """
        Classify the financial consequences of an action.

        Important limitation
        --------------------
        This method can classify transactions only when the
        corresponding action is available.

        If action is None, we can calculate cash-flow variation:

            current_cash - previous_cash

        but we deliberately do NOT classify that variation as
        income or expenses.

        This prevents incorrect accounting such as interpreting
        BUY_ANIMAL as a loss.
        """

        self.income = 0
        self.expenses = 0
        self.cash_flow = 0

        self.acquisition_cost = 0
        self.investment_return = 0
        self.last_transaction = None

        # =====================================================
        # NO ACTION AVAILABLE
        # =====================================================

        if action is None:

            if previous_cash is not None:

                self.cash_flow = (
                    self.cash - previous_cash
                )

            return

        # =====================================================
        # NORMALIZE MARKET ACTIONS
        # =====================================================

        market_orders = []

        if isinstance(action, dict):

            market_orders = action.get(
                'market',
                []
            )

        elif isinstance(action, list):

            market_orders = action

        # =====================================================
        # MARKET ORDERS
        # =====================================================

        for order in market_orders:

            if not order:
                continue

            operation = order[0]

            # -------------------------------------------------
            # BUY_SEED
            # -------------------------------------------------

            if operation == 'BUY_SEED':

                if len(order) < 3:
                    continue

                seed = order[1]
                quantity = order[2]

                price = self._seed_price(seed)

                cost = price * quantity

                self.expenses += cost

                self.last_transaction = {
                    'type': 'expense',
                    'operation': operation,
                    'item': seed,
                    'quantity': quantity,
                    'amount': cost,
                }

            # -------------------------------------------------
            # BUY_PRODUCT
            # -------------------------------------------------

            elif operation == 'BUY_PRODUCT':

                if len(order) < 3:
                    continue

                product = order[1]
                quantity = order[2]

                price = self.prices.get(
                    product,
                    0
                )

                cost = price * quantity

                self.expenses += cost

                self.last_transaction = {
                    'type': 'expense',
                    'operation': operation,
                    'item': product,
                    'quantity': quantity,
                    'amount': cost,
                }

            # -------------------------------------------------
            # BUY_ANIMAL
            # -------------------------------------------------

            elif operation == 'BUY_ANIMAL':

                if len(order) < 3:
                    continue

                animal = order[1]
                quantity = order[2]

                unit_cost = self.ANIMAL_COSTS.get(
                    animal,
                    0
                )

                cost = unit_cost * quantity

                self.expenses += cost

                # Animal acquisition is also recorded as an
                # investment because the animal remains a
                # productive asset.

                self.acquisition_cost += cost

                self.investments.setdefault(
                    'animals',
                    {
                        'type': 'productive_asset',
                        'acquisition_cost': 0,
                        'units': 0,
                        'return': 0,
                    }
                )

                self.investments[
                    'animals'
                ]['acquisition_cost'] += cost

                self.investments[
                    'animals'
                ]['units'] += quantity

                self.last_transaction = {
                    'type': 'investment',
                    'operation': operation,
                    'item': animal,
                    'quantity': quantity,
                    'amount': cost,
                }

            # -------------------------------------------------
            # SELL
            # -------------------------------------------------

            elif operation == 'SELL':

                if len(order) < 3:
                    continue

                product = order[1]
                quantity = order[2]

                price = self.prices.get(
                    product,
                    0
                )

                revenue = price * quantity

                self.income += revenue

                self.last_transaction = {
                    'type': 'income',
                    'operation': operation,
                    'item': product,
                    'quantity': quantity,
                    'amount': revenue,
                }

            # -------------------------------------------------
            # HIRE
            # -------------------------------------------------

            elif operation == 'HIRE':

                """
                Hiring is an operating expense.

                The price depends on hires_today.

                The current farm state represents the number of
                hires already made today, therefore the cost of
                the next hire is calculated from that value.
                """

                hires_today = self.me.get(
                    'hires_today',
                    0
                )

                cost = self._hire_cost(
                    hires_today
                )

                self.expenses += cost

                self.last_transaction = {
                    'type': 'expense',
                    'operation': operation,
                    'amount': cost,
                }

            # -------------------------------------------------
            # BUY_LAND
            # -------------------------------------------------

            elif operation == 'BUY_LAND':

                """
                Land acquisition is both:

                    - an expense/cash outflow
                    - an investment/fixed asset acquisition

                The current number of unlocked quadrants is used
                to determine which acquisition price applies.
                """

                unlocked = self.me.get(
                    'unlocked_quadrants',
                    ['NW']
                )

                extra_quadrants = max(
                    0,
                    len(unlocked) - 1
                )

                if extra_quadrants < len(
                    self.LAND_PRICES
                ):

                    cost = self.LAND_PRICES[
                        extra_quadrants
                    ]

                    self.expenses += cost

                    self.acquisition_cost += cost

                    self.investments.setdefault(
                        'land',
                        {
                            'type': 'fixed_asset',
                            'acquisition_cost': 0,
                            'units': 0,
                            'return': 0,
                        }
                    )

                    self.investments[
                        'land'
                    ]['acquisition_cost'] += cost

                    self.investments[
                        'land'
                    ]['units'] += 1

                    self.last_transaction = {
                        'type': 'investment',
                        'operation': operation,
                        'amount': cost,
                    }

        # =====================================================
        # FARMER / HAND ACTIONS
        # =====================================================

        unit_actions = []

        if isinstance(action, dict):

            if action.get('farmer'):
                unit_actions.append(
                    action['farmer']
                )

            for hand_action in action.get(
                'hands',
                []
            ):
                unit_actions.append(
                    hand_action
                )

        # =====================================================
        # BUILDINGS
        # =====================================================

        """
        Buildings are fixed assets.

        Their acquisition is therefore recorded as:

            expense
            +
            investment acquisition cost

        The exact building cost must correspond to the game
        action rules.
        """

        for unit_action in unit_actions:

            if not unit_action:
                continue

            operation = unit_action[0]

            if operation in (
                'BUILD_COOP',
                'BUILD_PASTURE',
            ):

                cost = 1

                self.expenses += cost

                self.acquisition_cost += cost

                structure = (
                    'coop'
                    if operation == 'BUILD_COOP'
                    else 'pasture'
                )

                self.investments.setdefault(
                    structure,
                    {
                        'type': 'fixed_asset',
                        'acquisition_cost': 0,
                        'units': 0,
                        'return': 0,
                    }
                )

                self.investments[
                    structure
                ]['acquisition_cost'] += cost

                self.investments[
                    structure
                ]['units'] += 1

                self.last_transaction = {
                    'type': 'investment',
                    'operation': operation,
                    'amount': cost,
                }

        # =====================================================
        # CASH FLOW
        # =====================================================

        """
        Cash flow represents the net financial movement produced
        by the transactions explicitly classified above.

            cash_flow =
                income - expenses

        When action is None, cash_flow is instead calculated from
        the actual variation of cash between observations.
        """

        self.cash_flow = (
            self.income
            - self.expenses
        )

        # =====================================================
        # INVESTMENT RETURN
        # =====================================================

        """
        IMPORTANT LIMITATION
        --------------------

        investment_return is currently an aggregate financial
        return, not the individual ROI of each asset.

        For example, if a cow produces milk and that milk is sold,
        we know that the farm generated income.

        However, a SELL action does not tell FinancialExpert
        exactly which cow, pasture, land quadrant or building
        generated that income.

        Therefore we cannot currently calculate reliably:

            cow #3 ROI
            pasture ROI
            land ROI
            building ROI

        without an additional attribution layer.

        The current implementation therefore keeps
        investment_return at the aggregate transaction level.

        Individual investment profitability is intentionally
        reserved for a second layer of financial analysis.
        """

        self.investment_return = (
            self.income
            - self.expenses
        )

        # =====================================================
        # PAYBACK
        # =====================================================

        """
        Payback

        The basic aggregate approximation is:

            payback =
                acquisition_cost
                / investment_return

        This is only meaningful when investment_return > 0.

        IMPORTANT LIMITATION
        --------------------

        This is NOT the individual payback period of an animal,
        land quadrant or building.

        Individual payback requires attribution of generated
        income to the corresponding investment.

        Therefore payback remains None when there is no positive
        aggregate return.
        """

        if self.acquisition_cost > 0:

            if self.investment_return > 0:

                self.payback = (
                    self.acquisition_cost
                    / self.investment_return
                )

            else:

                self.payback = None

        else:

            self.payback = None

    # =========================================================
    # SEED PRICE
    # =========================================================

    def _seed_price(self, seed):

        """
        Return the acquisition price of one seed.

        Seeds are valued separately from commercial inventory.

        The values correspond to the game's seed purchase prices.
        """

        seed_prices = {
            'WHEAT': 10,
            'CARROT': 20,
            'TOMATO': 50,
            'STRAWBERRY': 100,
            'MELON': 80,
        }

        return seed_prices.get(
            seed,
            0
        )

    # =========================================================
    # HIRE COST
    # =========================================================

    def _hire_cost(self, hires_today):

        """
        Return the cost of the next HIRE action.

        Hiring follows the Fibonacci sequence:

            first hire  -> 1
            second hire -> 1
            third hire  -> 2
            fourth hire -> 3
            fifth hire  -> 5
            ...

        hires_today represents the number of hires already made
        before the new hire.
        """

        a = 1
        b = 1

        for _ in range(hires_today):

            a, b = b, a + b

        return a


    # =========================================================
    # PUBLIC GETTERS
    # =========================================================

    def get_features(self):
        """
        Return all financial features exposed by FinancialExpert.

        This is the main interface that other Experts or the
        final ML/decision layer can use when they need the
        complete financial state.

        The returned dictionary contains values calculated by
        FinancialExpert but does not expose its internal
        implementation.
        """

        return {
            # -------------------------
            # Cash and financial flows
            # -------------------------

            'cash': self.cash,
            'income': self.income,
            'expenses': self.expenses,
            'cash_flow': self.cash_flow,

            # -------------------------
            # Inventory valuation
            # -------------------------

            'inventory_value': self.inventory_value,
            'seed_value': self.seed_value,

            # -------------------------
            # Productive assets
            # -------------------------

            'animals': self.animals.copy(),
            'animal_asset_value': self.animal_asset_value,
            'land_value': self.land_value,

            # -------------------------
            # Total financial position
            # -------------------------

            'assets': self.assets,
            'net_worth': self.net_worth,
            'balance': self.balance,

            # -------------------------
            # Liquidity
            # -------------------------

            'liquidity_ratio': self.liquidity_ratio,
            'money_per_day_remaining': (
                self.money_per_day_remaining
            ),

            # -------------------------
            # Investments
            # -------------------------

            'investments': self.investments.copy(),
            'acquisition_cost': self.acquisition_cost,
            'investment_return': self.investment_return,
            'payback': self.payback,

            # -------------------------
            # Last transaction
            # -------------------------

            'last_transaction': self.last_transaction,
        }


    def get_cash(self):
        """
        Return current available cash.
        """
        return self.cash


    def get_income(self):
        """
        Return income generated by the transaction currently
        being processed.
        """
        return self.income


    def get_expenses(self):
        """
        Return expenses generated by the transaction currently
        being processed.
        """
        return self.expenses


    def get_cash_flow(self):
        """
        Return the current net cash flow.

            cash_flow = income - expenses

        When no action is available, this can represent the
        observed change in cash between consecutive observations.
        """
        return self.cash_flow


    def get_inventory_value(self):
        """
        Return the current economic value of products stored
        in the shed.

        Animal units are excluded because animals are handled
        separately as productive assets.
        """
        return self.inventory_value


    def get_seed_value(self):
        """
        Return the economic value assigned to the player's
        currently stored seeds.
        """
        return self.seed_value


    def get_animals(self):
        """
        Return the current number of animals by type.

        Returns a copy so that another Expert cannot accidentally
        modify FinancialExpert's internal state.
        """
        return self.animals.copy()


    def get_animal_asset_value(self):
        """
        Return the acquisition-value representation of the
        player's current animals.
        """
        return self.animal_asset_value


    def get_land_value(self):
        """
        Return the acquisition value of the unlocked land.

        This is historical/acquisition value, not a predicted
        resale or market value.
        """
        return self.land_value


    def get_assets(self):
        """
        Return total non-cash assets.

            assets =
                inventory
                + seeds
                + animals
                + land
        """
        return self.assets


    def get_net_worth(self):
        """
        Return total net worth.

        Currently there are no liabilities modeled, therefore:

            net_worth = cash + assets
        """
        return self.net_worth


    def get_balance(self):
        """
        Return the current financial balance.

        Since liabilities are not currently modeled:

            balance = net_worth
        """
        return self.balance


    def get_liquidity_ratio(self):
        """
        Return the proportion of total net worth currently
        available as cash.

            liquidity_ratio = cash / net_worth
        """
        return self.liquidity_ratio


    def get_money_per_day_remaining(self):
        """
        Return the average amount of current cash available per
        remaining game day.

        This is a planning feature, not an accounting measure.
        """
        return self.money_per_day_remaining


    def get_investments(self):
        """
        Return the currently recorded investments.

        A copy is returned so external Experts cannot directly
        modify FinancialExpert's internal investment state.
        """
        return self.investments.copy()


    def get_acquisition_cost(self):
        """
        Return the acquisition cost detected for the investments
        processed in the current transaction.
        """
        return self.acquisition_cost


    def get_investment_return(self):
        """
        Return the aggregate financial return currently
        calculated by FinancialExpert.

        IMPORTANT
        ---------
        This is NOT the ROI of an individual asset.

        It does not tell us, for example:

            - ROI of one cow
            - ROI of one pasture
            - ROI of one land quadrant
            - ROI of one building

        Individual ROI requires attribution of generated income
        to the specific productive asset.
        """
        return self.investment_return


    def get_payback(self):
        """
        Return the currently calculated aggregate payback value.

        None means that a meaningful positive return is not
        currently available for calculating payback.
        """
        return self.payback


    def get_last_transaction(self):
        """
        Return the normalized representation of the last
        financial transaction processed.

        Returns None when no transaction was processed.
        """
        return self.last_transaction


    # =========================================================
    # TEMPORAL GETTERS
    # =========================================================

    def get_step(self):
        """
        Return the current game step.
        """
        return self.step


    def get_day(self):
        """
        Return the current game day.
        """
        return self.day


    def get_hour(self):
        """
        Return the current game hour.
        """
        return self.hour


    def get_days_remaining(self):
        """
        Return the number of game days remaining.
        """
        return self.days_remaining


    def get_steps_remaining(self):
        """
        Return the number of game steps remaining.
        """
        return self.steps_remaining


    def get_season_progress(self):
        """
        Return the normalized progress through the game season.

            0.0 -> beginning
            1.0 -> end
        """
        return self.season_progress


    def is_day_start_now(self):
        """
        Return True when the current observation corresponds
        to the beginning of a game day.
        """
        return self.is_day_start


    def is_day_end_now(self):
        """
        Return True when the current observation corresponds
        to the end of a game day.
        """
        return self.is_day_end


    def is_last_day_now(self):
        """
        Return True when the current observation is on the
        final game day.
        """
        return self.is_last_day


    def is_last_week_now(self):
        """
        Return True when seven or fewer game days remain.
        """
        return self.is_last_week



class AgricultureExpert:
    def __init__(self):
        pass

class LivestockExpert:
    def __init__(self):
        pass

class InventoryExpert:
    def __init__(self):
        pass

class MarketExpert:
    def __init__(self):
        pass

class OperationsExpert:
    def __init__(self):
        pass

class ProductionExpert:
    def __init(self):
        pass



