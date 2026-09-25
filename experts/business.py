class FinancialExpert:

    def __init__(self, player=0):
        self.player = player

        # Estado temporal
        self.step = None
        self.day = None
        self.hour = None

        # Estado financiero
        self.cash = 0
        self.shed = {}
        self.shed_value = 0

        # Mercado
        self.prices = {}

        # Mano de obra
        self.hands = []
        self.hires_today = 0

        # Historial
        self.previous_cash = None
        self.previous_shed = None

        # Activos productivos
        self.animals = {}

    def process_observation(self, obs):

        # -------------------------
        # Información general
        # -------------------------

        self.step = obs['step']
        self.day = obs['day']
        self.hour = obs['hour']

        # -------------------------
        # Datos propios del jugador
        # -------------------------

        self.me = obs['farms'][self.player]
        self.private = obs['private']

        self.cash = self.me['money']

        self.hands = self.me['hands']
        self.hires_today = self.me['hires_today']

        # -------------------------
        # Inventario
        # -------------------------

        self.shed = self.private['shed']

        # -------------------------
        # Mercado
        # -------------------------

        self.market = obs['market']
        self.prices = self.market['prices']

        # -------------------------
        # Valor del inventario
        # -------------------------

        self.shed_value = sum(
            self.prices.get(product, 0) * quantity
            for product, quantity in self.shed.items()
        )

        # -------------------------
        # Detectar animales
        # -------------------------

        animal_types = ['COW', 'SHEEP', 'GOOSE']

        for animal in animal_types:

            current_quantity = self.shed.get(animal, 0)

            previous_quantity = 0

            if self.previous_shed is not None:
                previous_quantity = self.previous_shed.get(animal, 0)

            new_animals = current_quantity - previous_quantity

            if new_animals > 0:

                for _ in range(new_animals):

                    animal_id = len(self.animals) + 1

                    self.animals[animal_id] = {
                        'type': animal,
                        'purchase_day': self.day,
                        'purchase_step': self.step,
                        'investment': None
                    }

        # -------------------------
        # Mostrar estado
        # -------------------------

        print(
            f"Step {self.step} | "
            f"Day {self.day} | "
            f"Hands: {len(self.hands)} | "
            f"Cash: ${self.cash:.2f} | "
            f"Shed value: ${self.shed_value:.2f}"
        )

        # -------------------------
        # Guardar estado anterior
        # -------------------------

        self.previous_cash = self.cash
        self.previous_shed = self.shed.copy()
