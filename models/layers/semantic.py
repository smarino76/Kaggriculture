class SemanticState:

    def __init__(
        self,
        financial_expert,
        agriculture_expert,
        inventory_expert,
        livestock_expert,
        market_expert,
    ):
        self.financial = financial_expert
        self.agriculture = agriculture_expert
        self.inventory = inventory_expert
        self.livestock = livestock_expert
        self.market = market_expert

        self.semantic = {}

    def process(self):
        """
        Interpreta el estado actual proporcionado
        por los Business Experts.
        """
        self.semantic = {
            "risks": {},
            "opportunities": {},
            "situations": {},
            "relationships": {},
        }

        # Aquí estarán nuestras reglas semánticas.

    def get_features(self):
        return self.semantic.copy()