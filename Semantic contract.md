# SemanticState — Feature Specification V1

## RISKS

| Nombre                          | Tipo           | Significado                                                                                                     | Expert(s)               | Getters reales                                                                 | Regla                                                                      | Información conservada                 | Utilidad ML                                                                   | Target leakage |
| ------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------- | -------------- |
| `liquidity_pressure`            | `float + bool` | Presión financiera sobre la capacidad de operar                                                                 | Financial               | `get_liquidity_ratio()`, `get_cash()`, `get_days_remaining()`                  | Determinar el nivel mediante una condición financiera que deberá definirse | Ratio + intensidad + contexto temporal | Permite aprender cuándo determinadas acciones son financieramente sostenibles | NO             |
| `storage_pressure`              | `float + bool` | Presión sobre la capacidad disponible del shed                                                                  | Inventory               | `get_shed_utilization()`, `get_shed_available()`                               | Derivar el nivel a partir de utilización/capacidad                         | Utilización + espacio restante         | Puede explicar decisiones de venta, transporte, producción, etc.              | NO             |
| `livestock_attention_required`  | `int + bool`   | Animales que requieren atención según su estado observado                                                       | Livestock               | `get_animal_details()`                                                         | Contar animales cuyo estado indique atención                               | Cantidad + detalle por animal          | Puede explicar acciones relacionadas con livestock                            | NO             |
| `production_storage_risk`       | `float + bool` | Riesgo generado cuando producción disponible y capacidad de almacenamiento están relacionadas desfavorablemente | Agriculture + Inventory | `get_production_ready_now()`, `get_shed_available()`, `get_shed_utilization()` | Relacionar producción lista con capacidad disponible                       | Producción + capacidad                 | Puede ser muy informativa para decisiones que afectan producción/inventario   | NO             |
| `liquidity_investment_pressure` | `float + bool` | Relación entre liquidez actual y capital comprometido en inversiones                                            | Financial               | `get_liquidity_ratio()`, `get_investments()`, `get_cash()`                     | Relacionar recursos líquidos con inversiones existentes                    | Cash + inversiones                     | Ayuda a distinguir capacidad económica de capacidad financiera inmediata      | NO             |

---

## OPPORTUNITIES

| Nombre                          | Tipo           | Significado                                                                        | Expert(s)                                    | Getters reales                                                                                                     | Regla                                                                        | Información conservada                       | Utilidad ML                                          | Target leakage |
| ------------------------------- | -------------- | ---------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------- | -------------- |
| `production_opportunity`        | `float + bool` | Existe producción que puede convertirse en recurso económico/operativo             | Agriculture + Inventory + Market             | `get_production_ready_now()`, `get_current_yield()`, `get_shed_available()`, `get_price()`                         | Relacionar producción disponible con almacenamiento y condiciones de mercado | Cantidad + capacidad + contexto de mercado   | Puede ayudar a modelos de harvest/sell/production    | NO             |
| `market_opportunity`            | `float + bool` | Condición de mercado potencialmente favorable respecto al estado actual            | Market + Inventory                           | `get_price()`, `get_price_change_pct()`, `get_price_trend()`, `get_market_pressure()` + inventario correspondiente | Combinar precio, tendencia y presión con recursos propios                    | Precio + dinámica + presión + disponibilidad | Permite aprender decisiones dependientes del mercado | NO             |
| `inventory_market_opportunity`  | `float + bool` | El jugador posee un producto y las condiciones de mercado pueden hacerlo relevante | Inventory + Market                           | `get_shed()`, `get_carried()`, `get_price()`, `get_price_trend()`, `get_market_pressure()`                         | Relacionar stock propio con estado de mercado                                | Producto + cantidad + mercado                | Muy útil para modelos de venta                       | NO             |
| `production_market_opportunity` | `float + bool` | Producción lista coincide con una condición de mercado potencialmente favorable    | Agriculture + Market                         | `get_production_ready_now()`, `get_price()`, `get_price_trend()`, `get_market_pressure()`                          | Relacionar producción con condiciones externas                               | Producción + mercado                         | Puede ayudar a decisiones de cosecha/venta           | NO             |
| `investment_opportunity`        | `float + bool` | Condición en la que una inversión puede ser económicamente relevante               | Financial + Market / Agriculture / Livestock | `get_cash()`, `get_investments()`, `get_animal_asset_value()`, `get_land_value()`, `get_acquisition_cost()`        | TBD: requiere definir qué consideramos oportunidad de inversión              | Recursos + inversión existente               | Puede ser útil para modelos de adquisición           | NO             |

---

## SITUATIONS

| Nombre                         | Tipo           | Significado                                      | Expert(s)   | Getters reales                                                                                         | Regla                                                   | Información conservada            | Utilidad ML                                                   | Target leakage |
| ------------------------------ | -------------- | ------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- | -------------- |
| `production_ready`             | `bool + int`   | Existe producción agrícola lista actualmente     | Agriculture | `get_production_ready_now()`, `get_ready_plants()`                                                     | Utilizar el estado ya determinado por AgricultureExpert | Existencia + cantidad             | Contexto fundamental para decisiones                          | NO             |
| `livestock_present`            | `bool + int`   | Estado actual del ganado del jugador             | Livestock   | `get_total_animals()`, `get_placed_animals()`, `get_shed_animals()`                                    | `total_animals > 0`                                     | Cantidad y distribución           | Contextualiza decisiones ganaderas/económicas                 | NO             |
| `livestock_attention_required` | `bool + int`   | Parte del livestock necesita atención            | Livestock   | `get_animal_details()`                                                                                 | Derivar desde `needs_feed` / estado observado           | Número + detalle                  | Puede anticipar necesidad de acciones sin codificar la acción | NO             |
| `storage_state`                | `categorical`  | Estado semántico del almacenamiento              | Inventory   | `get_shed_utilization()`, `get_shed_available()`                                                       | Clasificar utilización según umbrales definidos         | Magnitud + categoría              | Permite modelos que reaccionen al grado de ocupación          | NO             |
| `liquidity_state`              | `categorical`  | Situación de liquidez actual                     | Financial   | `get_liquidity_ratio()`, `get_cash()`, `get_days_remaining()`                                          | Clasificación basada en reglas definidas                | Ratio + cash + horizonte temporal | Contexto económico general                                    | NO             |
| `market_state`                 | `categorical`  | Situación actual del mercado para un producto    | Market      | `get_price_trend()`, `get_market_pressure()`, `get_equilibrium_position()`                             | Combinar tendencia + presión + posición                 | Dirección + intensidad + posición | Permite aprendizaje condicionado por mercado                  | NO             |
| `farm_capacity_state`          | `categorical`  | Estado de utilización de superficie agrícola     | Agriculture | `get_agricultural_surface()`, `get_occupied_agricultural_surface()`, `get_free_agricultural_surface()` | Relacionar ocupada/libre/total                          | Capacidad + ocupación             | Contextualiza plantación y expansión                          | NO             |
| `time_pressure`                | `float + bool` | Cuánto condiciona el horizonte temporal restante | Financial   | `get_days_remaining()`, `get_steps_remaining()`, `get_season_progress()`                               | Derivar del tiempo restante                             | Tiempo absoluto + progreso        | Muy importante para distinguir comienzo/final de partida      | NO             |

---

## RELATIONSHIPS

| Nombre                               | Tipo    | Significado                                                        | Expert(s)                        | Getters reales                                                                             | Regla                                                  | Información conservada              | Utilidad ML                                                             | Target leakage |
| ------------------------------------ | ------- | ------------------------------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------- | ----------------------------------------------------------------------- | -------------- |
| `production_storage_relationship`    | `float` | Relación entre producción disponible y capacidad de almacenamiento | Agriculture + Inventory          | `get_production_ready_now()`, `get_shed_available()`                                       | Comparar producción lista con capacidad disponible     | Ambos componentes + relación        | Puede revelar conflictos entre producir, almacenar y liberar inventario | NO             |
| `inventory_market_relationship`      | `float` | Relación entre inventario propio y condiciones de mercado          | Inventory + Market               | `get_shed()`, `get_carried()`, `get_price()`, `get_price_trend()`, `get_market_pressure()` | Relacionar stock con mercado                           | Stock + precio + dinámica + presión | Fundamental para aprender decisiones de mercado                         | NO             |
| `production_market_relationship`     | `float` | Relación entre producción disponible y mercado                     | Agriculture + Market             | `get_production_ready_now()`, `get_price()`, `get_price_trend()`, `get_market_pressure()`  | Relacionar producción con condiciones de mercado       | Producción + mercado                | Puede ayudar a decisiones de cosecha/venta                              | NO             |
| `liquidity_production_relationship`  | `float` | Relación entre liquidez y producción disponible                    | Financial + Agriculture          | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`                        | Combinar capacidad financiera y productiva             | Cash + liquidez + producción        | Permite aprender bajo restricciones económicas                          | NO             |
| `liquidity_market_relationship`      | `float` | Relación entre capacidad financiera y condiciones de mercado       | Financial + Market               | `get_cash()`, `get_liquidity_ratio()`, `get_price()`, `get_price_trend()`                  | Combinar liquidez y mercado                            | Recursos líquidos + mercado         | Puede ayudar a modelos de adquisición/venta                             | NO             |
| `livestock_financial_relationship`   | `float` | Relación entre posición ganadera y posición financiera             | Livestock + Financial            | `get_total_animals()`, `get_animal_asset_value()`, `get_cash()`, `get_liquidity_ratio()`   | Relacionar animales/valor y liquidez                   | Animales + valor + cash + liquidez  | Útil para decisiones relacionadas con livestock                         | NO             |
| `livestock_inventory_relationship`   | `float` | Relación entre animales y recursos físicos disponibles             | Livestock + Inventory            | `get_placed_animals()`, `get_shed_animals()`, `get_carried_animals()`, `get_shed()`        | Relacionar distribución de animales y recursos físicos | Ubicación + inventario              | Ayuda a interpretar estados operativos                                  | NO             |
| `financial_opportunity_relationship` | `float` | Relación entre recursos financieros y oportunidades detectadas     | Financial + Agriculture + Market | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`, `get_price_trend()`   | TBD                                                    | Recursos + oportunidades            | Puede ser potente para modelos de decisión                              | NO             |

---

# Candidatas V1

## RISKS

* `liquidity_pressure`
* `storage_pressure`
* `livestock_attention_required`
* `production_storage_risk`

## OPPORTUNITIES

* `production_opportunity`
* `market_opportunity`
* `inventory_market_opportunity`
* `production_market_opportunity`

## SITUATIONS

* `production_ready`
* `livestock_present`
* `storage_state`
* `liquidity_state`
* `market_state`
* `farm_capacity_state`
* `time_pressure`

## RELATIONSHIPS

* `production_storage_relationship`
* `inventory_market_relationship`
* `production_market_relationship`
* `liquidity_production_relationship`
* `livestock_financial_relationship`
* `livestock_inventory_relationship`

## Todavía TBD

* `investment_opportunity`
* `financial_opportunity_relationship`
* `animal_feed_shortage`
* `seed_purchase_affordable`

---

## Regla de implementación

**Ninguna feature se implementa hasta que estén verificadas:**

1. Sus fuentes.
2. Sus getters reales.
3. Su regla determinista.
4. La información que conserva.
5. Su utilidad para ML.
6. La ausencia de target leakage.

La SemanticState debe generar **información semántica e informativa**, no limitarse a copiar valores de los Business Experts ni codificar directamente las acciones que posteriormente deberán predecir los modelos.
