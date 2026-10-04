# SemanticState — Feature Specification V1.2

> **Estado:** formato estructural aprobado; las features y sus reglas siguen siendo candidatas en auditoría contra el código. Una feature aceptada conceptualmente aún no está implementada hasta validar getter, regla determinista, información retenida, granularidad, redundancia y leakage. `brainstorming.md` es ideación histórica; `Semantic pattern.md` es espacio de hipótesis, no especificación.

`SemanticState` es la capa donde viven las features semánticas y cross-domain validadas. Actualmente implementa situaciones de ganado, producción lista y capacidad agrícola; las relaciones de producción/almacenamiento y los riesgos de almacenamiento y producción/almacenamiento. Las demás candidatas siguen pendientes. Los hechos de dominio siguen perteneciendo a sus Business Experts. SemanticState describe el estado y no recomienda ni codifica acciones.

## Contrato estructural aprobado

La salida de `SemanticState.get_features()` contiene siempre las cuatro categorías siguientes. Cada categoría es un diccionario indexado por el nombre estable de la feature. Cada entrada de feature contiene exactamente la envoltura común `value` y `details`:

```python
{
    "situations": {
        "<feature_name>": {
            "value": ...,
            "details": {...},
        },
    },
    "relationships": {},
    "risks": {},
    "opportunities": {},
}
```

Reglas del contrato:

1. Las cuatro categorías existen siempre, aunque estén vacías.
2. Toda feature usa la misma envoltura: `value` para el resultado principal y `details` para las señales que lo contextualizan y explican.
3. `value` puede ser booleano cuando responde claramente si una condición semántica se cumple, pero un booleano aislado no se considera una representación suficientemente informativa. `details` debe conservar las magnitudes, componentes y contexto que permitan interpretar la condición; cuando sea aplicable, debe incluir su intensidad o grado, no solo repetir el booleano.
4. El tipo de `value` y las claves/tipos permitidos en `details` se especifican por feature en este contrato antes de implementarla. La envoltura común no implica que todas las features tengan el mismo tipo de valor.
5. Los datos de mercado, inventario o producción cuya fuente sea por producto conservan la identidad del producto dentro de `details`, usando una estructura `by_product` con nombres de producto como claves. No se promedian ni colapsan sin una regla explícita y validada.
6. `None` no se usa como marcador genérico de “regla no definida”. Una feature sin regla validada permanece fuera de la salida; los valores nulos solo se permiten si el contrato específico de esa feature les asigna un significado para datos ausentes/no observables.

Ejemplo de una feature por producto:

```python
{
    "opportunities": {
        "market_opportunity": {
            "value": True,
            "details": {
                "signal": "market_conditions",
                "by_product": {
                    "WHEAT": {
                        "price": 12,
                        "trend": "rising",
                        "price_change_pct": 0.08,
                    },
                },
            },
        },
    },
}
```

Este contrato fija la forma externa; no aprueba por sí mismo ninguna feature, umbral o regla del ejemplo. `Semantic pattern.md` debe tratar sus patrones como candidatos que, una vez validados, se expresarán con esta envoltura.

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
| `storage_pressure`              | `value: bool; details: {shed_utilization: float, shed_available: int, shed_capacity: int, shed_used: int}` | El cobertizo está lleno y no admite más artículos | Inventory | `get_shed_utilization()`, `get_shed_available()`, `get_shed_capacity()`, `get_shed_used()` | `value = shed_available == 0` | Utilización y capacidad restante/total | Describe una restricción física actual | TBD |
| `livestock_maintenance_risk`    | `value: bool; details: {animals_at_escape_risk: int, escape_rule_consecutive_unfed_days: int, animals: list[animal_detail]}` | Riesgo observable de que un animal colocado escape por falta de alimentación | Livestock | `get_animal_details()` | Activar si cualquier animal tiene `consecutive_unfed >= 1`; el juego elimina al animal al alcanzar 2 días consecutivos sin alimentar | Animales afectados y estado de alimentación observado | Señala una consecuencia próxima y verificable, distinta de la necesidad diaria de alimentar | TBD |
| `production_storage_risk`       | `value: bool; details: {production_storage_relationship: object, production_exceeding_available_storage: number}` | La producción lista supera el espacio libre del cobertizo | Agriculture + Inventory | Relación `production_storage_relationship` | `value = capacity_gap_units > 0`; derivar exclusivamente de la relación | Relación canónica y excedente en unidades | Identifica producción que no cabe en el espacio actual | TBD |
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
| `production_ready`             | `value: bool; details: {ready_plants: int, production_ready_now: number, by_product: dict[str,{ready_plants: int, yield_units: number}]}` | Existe producción agrícola lista actualmente | Agriculture | `get_crop_details()` | Una planta está lista cuando `is_ready` es verdadero (`yield_units > 0`); sumar plantas y unidades listas por producto | Booleano contextualizado con cantidad de plantas y rendimiento listo por producto | Contexto para modelos productivos | TBD |
| `livestock_present`            | `value: bool; details: {total_animals: int, placed_animals: dict[str,int], shed_animals: dict[str,int], carried_animals: dict[str,int]}` | Presencia actual de ganado del jugador | Livestock | `get_total_animals()`, `get_placed_animals()`, `get_shed_animals()`, `get_carried_animals()` | `value = total_animals > 0` | Conserva el total y distribución por ubicación para contextualizar el booleano | Contextualiza análisis ganadero/económico | NO |
| `livestock_attention`          | `value: bool; details: {animals_needing_feed: int, animals: list[animal_detail]}` | Animales colocados que muestran necesidad de alimentación | Livestock | `get_animal_details()` | Un animal requiere atención cuando el detalle observable indica `needs_feed` | Conteo y detalles de animales que cumplen la condición | Contexto operativo sin recomendar una acción | TBD |
| `storage_state`                | `value: float; details: {shed_used: int, shed_capacity: int, shed_available: int}` | Fracción actual de capacidad de almacenamiento utilizada | Inventory | `get_shed_utilization()`, `get_shed_available()`, `get_shed_capacity()`, `get_shed_used()` | `value = shed_used / shed_capacity` según el getter del experto; el valor está entre 0 y 1 | Utilización continua y magnitudes que la explican | Da el grado de ocupación sin imponer categorías o umbrales arbitrarios | TBD |
| `liquidity_state`              | `categorical`  | Situación de liquidez actual                     | Financial   | `get_liquidity_ratio()`, `get_cash()`, `get_days_remaining()`                                          | Clasificación basada en reglas definidas                | Ratio + cash + horizonte temporal | Contexto económico general                                    | NO             |
| `market_state`                 | `categorical`  | Situación actual del mercado para cada producto | Market      | Getters de Market que reciben `product`                                                           | Combinar tendencia + presión + posición; regla TBD       | Por producto; dirección + intensidad + posición | Permite aprendizaje condicionado por mercado | TBD |
| `farm_capacity_state`          | `value: float; details: {agricultural_surface: int, occupied_surface: int, crop_surface: int, weed_surface: int, free_surface: int}` | Fracción de superficie agrícola no libre (cultivos o maleza) | Agriculture | `get_agricultural_surface()`, `get_occupied_agricultural_surface()`, `get_weed_agricultural_surface()`, `get_free_agricultural_surface()` | `occupied_surface = crop_surface + weed_surface`; `value = occupied_surface / agricultural_surface`; si la superficie es cero, `0.0` | Proporción y desglose de superficie total, cultivos, maleza y superficie libre | Contextualiza el margen físico de cultivo sin umbrales arbitrarios | TBD |
| `time_pressure`                | `float + bool` | Interpretación de cuánto condiciona el horizonte restante | Financial | `get_days_remaining()`, `get_steps_remaining()`, `get_season_progress()` | TBD; el tiempo observado no determina por sí solo un nivel de presión | Tiempo absoluto + progreso | Puede distinguir contexto temporal | TBD |

---

## RELATIONSHIPS

| Nombre                               | Tipo    | Significado                                                        | Expert(s)                        | Getters reales                                                                             | Regla                                                  | Información conservada              | Utilidad ML                                                             | Target leakage |
| ------------------------------------ | ------- | ------------------------------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------- | ----------------------------------------------------------------------- | -------------- |
| `production_storage_relationship`    | `value: number; details: {production_ready_now: number, shed_available: int, shed_used: int, shed_capacity: int, capacity_gap_units: number}` | Diferencia entre producción lista y espacio libre | Agriculture + Inventory | `get_production_ready_now()`, `get_shed_available()`, `get_shed_used()`, `get_shed_capacity()` | `value = production_ready_now - shed_available`; positivo indica excedente, negativo indica espacio sobrante | Ambas magnitudes y diferencia firmada | Cuantifica el ajuste entre producción lista y almacenamiento disponible | TBD |
| `inventory_market_relationship`      | `value: bool; details: {products_with_inventory: int, by_product: dict[str,{inventory_quantity: number, market_available: bool, price: number\|None, price_change_pct: number, price_trend: str, market_pressure: number\|None, equilibrium_position: str\|None}]}` | Inventario propio y condiciones de mercado asociadas por producto | Inventory + Market | `get_total_physical()`, `get_price(product)`, `get_price_change_pct(product)`, `get_price_trend(product)`, `get_market_pressure(product)`, `get_equilibrium_position(product)` | Por cada producto con cantidad física positiva, conservar inventario y señales de mercado; `value` indica si hay al menos un producto | Cantidad y condiciones de mercado por producto; `market_available=false` y `price=null` indican que falta precio observable | Permite analizar existencias bajo distintas condiciones de mercado | TBD |
| `production_market_relationship`     | `value: bool; details: {products_with_ready_production: int, by_product: dict[str,{ready_plants: int, yield_units: number, market_available: bool, price: number\|None, price_change_pct: number, price_trend: str, market_pressure: number\|None, equilibrium_position: str\|None}]}` | Producción lista y condiciones de mercado asociadas por producto | Agriculture + Market | `get_crop_details()`, `get_price(product)`, `get_price_change_pct(product)`, `get_price_trend(product)`, `get_market_pressure(product)`, `get_equilibrium_position(product)` | Para cada cultivo con producción lista, conservar cantidad y señales de mercado de ese producto; `value` indica si existe producción lista | Unidades y cantidad de plantas listas junto con el contexto del mercado por producto; `market_available=false` y `price=null` indican que falta precio observable | Permite analizar producción lista bajo distintas condiciones de mercado, sin estimar ingresos ni recomendar una acción | TBD |
| `liquidity_production_relationship`  | `float` | Relación entre liquidez y producción disponible                    | Financial + Agriculture          | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`                        | Combinar capacidad financiera y productiva             | Cash + liquidez + producción        | Permite aprender bajo restricciones económicas                          | NO             |
| `liquidity_market_relationship`      | `dict[product]` | Relación entre liquidez y condiciones de mercado por producto | Financial + Market | `get_cash()`, `get_liquidity_ratio()`, Market getters con `product` | Regla y significado TBD | Por producto; recursos + mercado | Puede ayudar a análisis condicionado por mercado | TBD |
| `livestock_financial_relationship`   | `float` | Relación entre posición ganadera y posición financiera             | Livestock + Financial            | `get_total_animals()`, `get_animal_asset_value()`, `get_cash()`, `get_liquidity_ratio()`   | Relacionar animales/valor y liquidez                   | Animales + valor + cash + liquidez  | Útil para decisiones relacionadas con livestock                         | NO             |
| `livestock_inventory_relationship`   | `float` | Relación entre animales y recursos físicos disponibles             | Livestock + Inventory            | `get_placed_animals()`, `get_shed_animals()`, `get_carried_animals()`, `get_shed()`        | Relacionar distribución de animales y recursos físicos | Ubicación + inventario              | Ayuda a interpretar estados operativos                                  | NO             |
| `financial_opportunity_relationship` | `float` | Relación entre recursos financieros y oportunidades detectadas     | Financial + Agriculture + Market | `get_cash()`, `get_liquidity_ratio()`, `get_production_ready_now()`, `get_price_trend()`   | TBD                                                    | Recursos + oportunidades            | Puede ser potente para modelos de decisión                              | NO             |

---

# Candidatas V1

## Implementadas

* `situations.livestock_present`
* `situations.production_ready`
* `situations.livestock_attention`
* `situations.farm_capacity_state`
* `situations.storage_state`
* `relationships.production_storage_relationship`
* `relationships.inventory_market_relationship`
* `relationships.production_market_relationship`
* `risks.storage_pressure`
* `risks.production_storage_risk`
* `risks.livestock_maintenance_risk`

## RISKS

* `liquidity_pressure`

## OPPORTUNITIES

* `production_opportunity`
* `market_opportunity`
* `inventory_market_opportunity`
* `production_market_opportunity`

## SITUATIONS

* `liquidity_state`
* `market_state`
* `time_pressure`

## RELATIONSHIPS

* `liquidity_production_relationship`
* `livestock_financial_relationship`
* `livestock_inventory_relationship`

Market-related relationships are product-keyed; no global average is implied.

## Todavía TBD

* `investment_opportunity`
* `financial_opportunity_relationship`
* Meaning and rule for `time_pressure` and `liquidity_pressure`
* Thresholds for categorical `liquidity_state` and `market_state`
* Sources and rules for remaining per-product opportunity features

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
