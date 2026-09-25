


def extract_time_features(data):
    """
        Extrae las features relacionadas con el tiempo de una observacion.

        La observacion debe contener la identidad del jugador, el dia actual y
        el turno dentro del dia. ``step`` es opcional: si no esta presente, se
        calcula usando 24 turnos por dia.

    Args:
                data (dict): Observacion del entorno. Debe contener:
                        - ``player`` (int): Identificador del jugador, normalmente 0 o 1.
                        - ``hour`` (int): Turno dentro del dia, de 0 a 23.
                        - ``day`` (int): Dia del episodio, comenzando en 0.
                        - ``step`` (int, optional): Turno global del episodio. Si falta,
                            se calcula como ``day * 24 + hour``.

        Returns:
                dict: Diccionario con las siguientes features:
                        - ``player`` (int): Identificador del jugador.
                        - ``hour`` (int): Turno actual dentro del dia.
                        - ``day`` (int): Dia actual del episodio.
                        - ``step`` (int): Turno global actual del episodio.
                        - ``days_remaining`` (int): Dias restantes, contando el dia
                            actual. Con la configuracion por defecto es ``30 - day``.
                        - ``steps_remaining`` (int): Turnos restantes. Con la
                            configuracion por defecto es ``720 - step``.
                        - ``is_day_ending`` (int): 1 si el turno es 22 o posterior;
                            en caso contrario, 0.
                        - ``is_day_starting`` (int): 1 si el turno es anterior a 6;
                            en caso contrario, 0.
                        - ``is_last_day`` (int): 1 si es el dia 29, el ultimo dia con
                            la configuracion por defecto; en caso contrario, 0.
                        - ``is_first_day`` (int): 1 si es el dia 0; en caso contrario, 0.

        Raises:
                ValueError: Si falta ``player``, ``hour`` o ``day`` en la
                        observacion.
    """
    
    player = data.get("player", -1)
    
    if player == -1:
        raise ValueError("Player information is missing in the data observation.")
    
    hour = data.get("hour", -1)
    
    if hour == -1:
        raise ValueError("Hour information is missing in the data observation.")
    
    day = data.get("day", -1)
    
    if day == -1:
        raise ValueError("Day information is missing in the data observation.")
    
    
    step = data.get("step", day * 24 + hour)
    
    return {
        "player": player,
        "hour": hour,
        "day": day,
        "step": step,
        "days_remaining": max(0, 30 - day),
        "steps_remaining": max(0, 720 - step),
        "is_day_ending": 1 if hour >= 22 else 0,
        "is_day_starting": 1 if hour < 6 else 0,
        "is_last_day": 1 if day == 29 else 0,
        "is_first_day": 1 if day == 0 else 0,
    }
    
    
    
def extract_economy_features(farm):
    """Extrae los datos economicos y operativos brutos de una granja.

    Args:
        farm (dict): Granja de un jugador. Debe contener ``money``,
            ``farmer``, ``hands``, ``unlocked_quadrants`` y ``hires_today``.

    Returns:
                dict: Diccionario con los valores brutos y sinteticos de la granja:
            - ``money`` (float): Dinero disponible del jugador.
            - ``farmer`` (list): Posicion ``[x, y]`` del granjero principal.
            - ``hands`` (list): Posiciones de los trabajadores contratados.
            - ``unlocked_quadrants`` (list): Cuadrantes de terreno comprados.
            - ``hires_today`` (int): Trabajadores contratados durante el dia.
                        - ``farmer_x`` (int): Coordenada horizontal del granjero principal.
                        - ``farmer_y`` (int): Coordenada vertical del granjero principal.
                        - ``hands_count`` (int): Cantidad de trabajadores contratados.
                        - ``unlocked_quadrant_count`` (int): Cantidad de cuadrantes
                            desbloqueados.
                        - ``has_hands`` (int): 1 si hay al menos un trabajador contratado;
                            en caso contrario, 0.
                        - ``has_full_land`` (int): 1 si los cuatro cuadrantes estan
                            desbloqueados; en caso contrario, 0.
    """
    money = farm["money"]
    farmer = farm["farmer"]
    hands = farm["hands"]
    unlocked_quadrants = farm["unlocked_quadrants"]
    hires_today = farm["hires_today"]

    hands_count = len(hands)
    unlocked_quadrant_count = len(unlocked_quadrants)

    return {
        # Features brutas
        "money": money,
        "farmer": farmer,
        "hands": hands,
        "unlocked_quadrants": unlocked_quadrants,
        "hires_today": hires_today,

        # Features sintéticas
        "farmer_x": farmer[0],
        "farmer_y": farmer[1],
        "hands_count": hands_count,
        "unlocked_quadrant_count": unlocked_quadrant_count,
        "has_hands": int(hands_count > 0),
        "has_full_land": int(unlocked_quadrant_count == 4),
    }
    
    
    def extract_inventory_features(data):
        shed = data.get("private", {}).get("shed", {})
        inventories = data.get("private", {}).get("inventories", {})
        seeds = data.get("private", {}).get("seeds", {})
        
        player = data["player"]
        my_farm = data["farms"][player]
        hands = my_farm["hands"]
        hands_count = len(hands)
        inventory_farmer = inventories[0]

        
        