# SemanticState — Feature Specification V1.1 (Candidate Contract)

> **Estado:** contrato candidato en auditoría contra el código. Una feature aceptada conceptualmente aún no está implementada hasta validar getter, regla determinista, información retenida, granularidad, redundancia y leakage. `brainstorming.md` es ideación histórica; `Semantic pattern.md` es espacio de hipótesis, no especificación.

`SemanticState` es la capa donde viven las features semánticas y cross-domain validadas. Actualmente es un esqueleto con `situations`, `relationships`, `risks` y `opportunities` vacíos. Los hechos de dominio siguen perteneciendo a sus Business Experts. SemanticState describe el estado y no recomienda ni codifica acciones.

## Dimensiones y límites de información

| Dimensión | Significado y límite |
| --- | --- |
| `own` | Hechos de nuestros expertos Financial, Agriculture, Inventory y Livestock. |
| `opponent_public` | Solo campos visibles entregados por `OpponentExpert`; no incluye inventario privado ni net worth completo. |
| `relative` | Diferencia/comparación own vs opponent_public; candidata futura, no implementada. |
| `temporal` | Tiempo actual o cambios derivados de observaciones; las reglas interpretativas requieren definición. |
| `competitive` | Interpretación de posición/trajectory relativa; StrategicExpert futuro, no implementado. |
| `market` | Condiciones externas del mercado; sus datos son por producto y no deben confundirse con dimensiones own/opponent. |

Mercado, inventario y producción vinculados al mercado deben conservar claves de producto. No colapsarlos en una media o escalar global sin una regla de agregación explícita y validada.

| Cobertura candidata | Dimensión | Límite |
| --- | --- | --- |
| Estado financiero, agrícola, inventario y ganadero propio | `own` | Hechos de los expertos propios; el valor económico sigue siendo responsabilidad de FinancialExpert. |
| Cash, tiles, cultivos/producción visible y animales colocados del rival | `opponent_public` | Solo valores efectivamente expuestos por OpponentExpert; no inventario privado ni patrimonio neto total. |
| Diferencias entre hechos propios y públicos comparables | `relative` | Futuro; comparar solo magnitudes compatibles y registrar datos ausentes. |
| Día, steps y cambios entre observaciones | `temporal` | El valor observado puede conservarse; presión/tendencia semántica requiere regla definida. |
| Posición y trayectoria competitiva | `competitive` | Futuro; responsabilidad prevista de StrategicExpert, sin recomendaciones de acción. |
| Precio, tendencia, presión y equilibrio | `market` | Externo y por producto; no atribuirlo al estado propio ni promediar productos arbitrariamente. |

Los `NO` heredados en la columna de target leakage son hipótesis del borrador, no resultados de una auditoría completa; hasta validar cada feature deben leerse como `TBD`.

## RISKS

| Nombre                          | Tipo           | Significado                                                                                                     | Expert(s)               | Getters reales                                                                 | Regla                                                                      | Información conservada                 | Utilidad ML                                                                   | Target leakage |
| ------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------- | -------------- |
| `liquidity_pressure`            | `float + bool` | Presión financiera sobre la capacidad de operar                                                                 | Financial               | `get_liquidity_ratio()`, `get_cash()`, `get_days_remaining()`                  | Determinar el nivel mediante una condición financiera que deberá definirse | Ratio + intensidad + contexto temporal | Permite aprender cuándo determinadas acciones son financieramente sostenibles | NO             |
| `storage_pressure`              | `float + bool` | Presión sobre la capacidad disponible del shed                                                                  | Inventory               | `get_shed_utilization()`, `get_shed_available()`                               | Derivar el nivel a partir de utilización/capacidad                         | Utilización + espacio restante         | Puede explicar decisiones de venta, transporte, producción, etc.              | NO             |
| `livestock_maintenance_risk`    | `bool + details` | Riesgo de mantenimiento inferido de una situación de atención ya validada                                        | Livestock               | `get_animal_details()`                                                         | TBD; debe ser distinto de la situación de atención                           | Situación base + interpretación       | Puede representar consecuencia contextual sin duplicar el hecho               | TBD            |
| `production_storage_risk`       | `float + bool` | Interpretación de riesgo derivada de la relación canónica producción/almacenamiento                              | Agriculture + Inventory | Relación `production_storage_relationship`                                    | Derivar de la relación validada; no recalcular fuentes independientemente    | Relación + interpretación              | Puede representar presión sobre cosecha/almacenamiento                         | TBD            |
| `liquidity_investment_pressure` | `float + bool` | Relación entre liquidez actual y capital comprometido en inversiones                                            | Financial               | `get_liquidity_ratio()`, `get_investments()`, `get_cash()`                     | Relacionar recursos líquidos con inversiones existentes                    | Cash + inversiones                     | Ayuda a distinguir capacidad económica de capacidad financiera inmediata      | NO             |

---

## OPPORTUNITIES

| Nombre                          | Tipo           | Significado                                                                        | Expert(s)                                    | Getters reales                                                                                                     | Regla                                                                        | Información conservada                       | Utilidad ML                                          | Target leakage |
| ------------------------------- | -------------- | ---------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------- | -------------- |
| `production_opportunity`        | `float + bool` | Producción disponible y condiciones de almacenamiento/mercado relevantes por producto | Agriculture + Inventory + Market          | Getters de producción, capacidad y `get_price(product)`                        | TBD; conservar producto y componentes                                       | Por producto; cantidad + contexto       | Puede apoyar análisis de producción/venta             | TBD            |
| `market_opportunity`            | `float + bool` | Condiciones del mercado potencialmente favorables por producto, sin incorporar inventario propio | Market | `get_price(product)`, `get_price_change_pct(product)`, `get_price_trend(product)`, `get_market_pressure(product)` | Regla aún no definida; solo condiciones externas | Por producto; precio + dinámica + presión | Distingue señal de mercado de oportunidad propia | TBD |
| `inventory_market_opportunity`  | `float + bool` | Inventario propio relacionado con mercado por producto                            | Inventory + Market                           | Getters de inventario por producto + Market getters con `product`               | TBD; no usar stock total × precio medio                                     | Por producto; stock + mercado            | Puede apoyar modelos de venta                         | TBD            |
| `production_market_opportunity` | `float + bool` | Producción de un producto relacionada con sus condiciones de mercado              | Agriculture + Market                         | Producción por producto + Market getters con `product`                          | TBD; no mezclar productos                                                   | Por producto; producción + mercado       | Puede apoyar análisis de cosecha/venta                 | TBD            |
| `investment_opportunity`        | `float + bool` | Condición en la que una inversión puede ser económicamente relevante               | Financial + Market / Agriculture / Livestock | `get_cash()`, `get_investments()`, `get_animal_asset_value()`, `get_land_value()`, `get_acquisition_cost()`        | TBD: requiere definir qué consideramos oportunidad de inversión              | Recursos + inversión existente               | Puede ser útil para modelos de adquisición           | NO             |

---

## SITUATIONS

| Nombre                         | Tipo           | Significado                                      | Expert(s)   | Getters reales                                                                                         | Regla                                                   | Información conservada            | Utilidad ML                                                   | Target leakage |
| ------------------------------ | -------------- | ------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- | -------------- |
| `production_ready`             | `bool + int`   | Existe producción agrícola lista actualmente     | Agriculture | `get_production_ready_now()`, `get_ready_plants()`                                                     | HOLD: el código actual suma `yield_units` de cada planta a `production_ready_now`, sin condicionar por `is_ready`; getter y significado no coinciden claramente | Existencia + cantidad | Contexto fundamental para decisiones | TBD |
| `livestock_present`            | `bool + int`   | Estado actual del ganado del jugador             | Livestock   | `get_total_animals()`, `get_placed_animals()`, `get_shed_animals()`                                    | `total_animals > 0`                                     | Cantidad y distribución           | Contextualiza decisiones ganaderas/económicas                 | NO             |
| `livestock_attention`          | `bool + int`   | Animales que presentan una condición observable de atención | Livestock | `get_animal_details()` | Contar y conservar detalles basados en estado observado | Número + detalle | Contexto para modelos sin codificar una acción | NO |
| `storage_state`                | `categorical`  | Estado semántico del almacenamiento              | Inventory   | `get_shed_utilization()`, `get_shed_available()`                                                       | Clasificar utilización según umbrales definidos         | Magnitud + categoría              | Permite modelos que reaccionen al grado de ocupación          | NO             |
| `liquidity_state`              | `categorical`  | Situación de liquidez actual                     | Financial   | `get_liquidity_ratio()`, `get_cash()`, `get_days_remaining()`                                          | Clasificación basada en reglas definidas                | Ratio + cash + horizonte temporal | Contexto económico general                                    | NO             |
| `market_state`                 | `categorical`  | Situación actual del mercado para cada producto | Market      | Getters de Market que reciben `product`                                                           | Combinar tendencia + presión + posición; regla TBD       | Por producto; dirección + intensidad + posición | Permite aprendizaje condicionado por mercado | TBD |
| `farm_capacity_state`          | `categorical`  | Estado de utilización de superficie agrícola     | Agriculture | `get_agricultural_surface()`, `get_occupied_agricultural_surface()`, `get_free_agricultural_surface()` | Relacionar ocupada/libre/total                          | Capacidad + ocupación             | Contextualiza plantación y expansión                          | NO             |
| `time_pressure`                | `float + bool` | Interpretación de cuánto condiciona el horizonte restante | Financial | `get_days_remaining()`, `get_steps_remaining()`, `get_season_progress()` | TBD; el tiempo observado no determina por sí solo un nivel de presión | Tiempo absoluto + progreso | Puede distinguir contexto temporal | TBD |

---

## RELATIONSHIPS

| Nombre                               | Tipo    | Significado                                                        | Expert(s)                        | Getters reales                                                                             | Regla                                                  | Información conservada              | Utilidad ML                                                             | Target leakage |
| ------------------------------------ | ------- | ------------------------------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------- | ----------------------------------------------------------------------- | -------------- |
| `production_storage_relationship`    | `structured` | Relación entre producción disponible y capacidad de almacenamiento | Agriculture + Inventory | `get_production_ready_now()`, `get_shed_available()` | Elegir entre componentes, diferencia, ratio o capacity gap; decisión abierta | Producción + capacidad + derivado | Puede revelar conflicto producción/almacenamiento | TBD |
| `inventory_market_relationship`      | `dict[product]` | Inventario propio y condiciones de mercado por producto | Inventory + Market | Getters de inventario por producto + Market getters con `product` | Relacionar stock y mercado manteniendo claves de producto | Por producto; stock + precio + dinámica + presión | Puede apoyar análisis de mercado | TBD |
| `production_market_relationship`     | `dict[product]` | Producción disponible y mercado por producto | Agriculture + Market | Producción por producto + Market getters con `product` | Relacionar producción y mercado sin agregación arbitraria | Por producto; producción + mercado | Puede apoyar análisis de cosecha/venta | TBD |
| `liquidity_production_relationship`  | `float` | Relación entre liquidez y producción disponible                    | Financial + Agriculture          | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`                        | Combinar capacidad financiera y productiva             | Cash + liquidez + producción        | Permite aprender bajo restricciones económicas                          | NO             |
| `liquidity_market_relationship`      | `dict[product]` | Relación entre liquidez y condiciones de mercado por producto | Financial + Market | `get_cash()`, `get_liquidity_ratio()`, Market getters con `product` | Regla y significado TBD | Por producto; recursos + mercado | Puede ayudar a análisis condicionado por mercado | TBD |
| `livestock_financial_relationship`   | `float` | Relación entre posición ganadera y posición financiera             | Livestock + Financial            | `get_total_animals()`, `get_animal_asset_value()`, `get_cash()`, `get_liquidity_ratio()`   | Relacionar animales/valor y liquidez                   | Animales + valor + cash + liquidez  | Útil para decisiones relacionadas con livestock                         | NO             |
| `livestock_inventory_relationship`   | `float` | Relación entre animales y recursos físicos disponibles             | Livestock + Inventory            | `get_placed_animals()`, `get_shed_animals()`, `get_carried_animals()`, `get_shed()`        | Relacionar distribución de animales y recursos físicos | Ubicación + inventario              | Ayuda a interpretar estados operativos                                  | NO             |
| `financial_opportunity_relationship` | `float` | Relación entre recursos financieros y oportunidades detectadas     | Financial + Agriculture + Market | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`, `get_price_trend()`   | TBD                                                    | Recursos + oportunidades            | Puede ser potente para modelos de decisión                              | NO             |

---

# Candidatas V1

## RISKS

* `liquidity_pressure`
* `storage_pressure`
* `production_storage_risk`
* `livestock_maintenance_risk` (rule TBD; distinct from attention situation)

## OPPORTUNITIES

* `production_opportunity`
* `market_opportunity`
* `inventory_market_opportunity`
* `production_market_opportunity`

## SITUATIONS

* `production_ready`
* `livestock_present`
* `livestock_attention`
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

Market-related relationships are product-keyed; no global average is implied.

## Todavía TBD

* `investment_opportunity`
* `financial_opportunity_relationship`
* Meaning and rule for `time_pressure` and `liquidity_pressure`
* Thresholds for categorical `storage_state` and other classifications
* Canonical representation for `production_storage_relationship`
* Per-product sources and rules for inventory/production-market features
* Whether `current_yield` and `production_ready_now` should be distinct; current code accumulates them identically

---

## Regla de implementación

**Ninguna feature se implementa hasta que estén verificadas:**

1. Sus fuentes.
2. Sus getters reales.
3. Su regla determinista.
4. La información que conserva.
5. Su producto/granularidad y dimensión (`own`, `opponent_public`, `relative`, `temporal`, `competitive`, or `market`).
6. Su utilidad para ML.
7. La ausencia de target leakage y duplicación.

La SemanticState debe generar **información semántica e informativa**, no limitarse a copiar valores de los Business Experts ni codificar directamente las acciones que posteriormente deberán predecir los modelos.
