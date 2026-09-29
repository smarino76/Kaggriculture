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

        # Las reglas semánticas se implementarán
        # únicamente después de validar:
        # - fuente
        # - getter
        # - regla determinista
        # - significado
        # - utilidad ML
        # - ausencia de leakage

    def get_features(self):
        return self.semantic.copy()