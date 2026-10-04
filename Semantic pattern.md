# Semantic Pattern Space — Kaggriculture

> **Estado:** espacio de hipótesis, no especificación de features. `SemanticState` implementa actualmente `situations.livestock_present`, `situations.production_ready`, `situations.livestock_attention`, `situations.storage_state`, `situations.farm_capacity_state`, `relationships.production_storage_relationship`, `relationships.inventory_market_relationship`, `relationships.production_market_relationship`, `risks.storage_pressure`, `risks.production_storage_risk` y `risks.livestock_maintenance_risk`; ningún otro patrón de este documento se considera implementado por aparecer aquí.

## 1. Purpose

El **Semantic Pattern Space** define el conjunto de posibles patrones semánticos que pueden ser construidos a partir de las señales producidas por los Business Experts.

No representa todavía la implementación de `SemanticState`.

Su objetivo es explorar de forma sistemática las combinaciones de información que pueden representar:

* estados;
* eventos;
* oportunidades;
* riesgos;
* alarmas;
* presiones;
* conflictos;
* sinergias;
* relaciones entre dominios.

El espacio de patrones puede ser deliberadamente más amplio que el conjunto final de features implementadas.

Los patrones deberán ser posteriormente validados antes de entrar en `SemanticState`.

## Contrato de salida de SemanticState

El formato externo de salida ya está aprobado y se define en `Semantic contract.md`. Toda feature candidata que supere la validación deberá usar la envoltura común:

```python
{
    "<category>": {
        "<feature_name>": {
            "value": ...,
            "details": {...},
        },
    },
}
```

`<category>` es una de `situations`, `relationships`, `risks` u `opportunities`. El tipo de `value` y el esquema de `details` deben documentarse para cada feature en el contrato antes de implementarla. `value` puede ser booleano para expresar si se cumple una condición, pero no debe ser la única información: `details` conserva las señales y magnitudes necesarias para contextualizar e interpretar el resultado. Cuando las señales sean por producto, `details` conserva esa granularidad bajo `by_product`. La presencia de un patrón en este documento no autoriza su implementación ni define por sí sola el tipo de sus campos.

---

# 2. Architecture

```text
RAW OBSERVATION
   ↓
SIX IMPLEMENTED BUSINESS EXPERTS
   ↓
DOMAIN FACTS
   ↓
VALIDATION OF CANDIDATE PATTERNS
   ↓
SEMANTIC STATE
  ├── situations
  ├── relationships
  ├── risks
  └── opportunities
   ↓
MODEL-SPECIFIC FEATURES
   ↓
SPECIALIZED DECISION EXPERTS
   ↓
DECISION COORDINATOR
   ↓
ACTION
```

Los Business Experts describen hechos de dominios específicos.

`SemanticState` combina e interpreta esos hechos para representar situaciones de negocio.

Los modelos posteriores utilizan esta representación para aprender relaciones entre estados, acciones y consecuencias.

---

# 3. Design Principles

## 3.1 Domain-driven

Cada señal debe proceder de información perteneciente a un dominio concreto.

Los dominios actuales son:

* Financial
* Agriculture
* Inventory
* Market
* Livestock
* Opponent public state
* Temporal context

`OpponentExpert` is implemented and restricted to observable public farm state. Relative/competitive interpretation is future work; private opponent fields are excluded from inference features.

Candidate features should state which dimensions they represent: `own`, `opponent_public`, `relative`, `temporal`, `competitive` and, where applicable, external `market` conditions. These dimensions are not interchangeable; do not imply opponent net worth where only public cash and visible farm facts exist.

Market, inventory and production-market patterns must preserve product identity when their source values are product-specific. Do not replace per-product information with an arbitrary average or scalar aggregate.

The current `AgricultureExpert` implementation accumulates `current_yield` and `production_ready_now` using the same per-plant `yield_units` rule. Treat them as redundant until their semantics or implementation diverge.

---

## 3.2 Informative

Un patrón debe aportar información útil para comprender el estado del negocio.

No se deben crear combinaciones únicamente porque matemáticamente sean posibles.

---

## 3.3 Deterministic

La interpretación semántica debe poder expresarse mediante reglas deterministas verificables.

No se debe utilizar ML dentro de `SemanticState` para decidir qué significa una situación.

---

## 3.4 No target leakage

Un patrón no debe contener directa o indirectamente la respuesta que posteriormente deberá aprender un modelo.

Por ejemplo, si el target es:

```text
BUY_COW
```

SemanticState puede representar:

```text
liquidity
livestock_present
animal_asset_value
market conditions
investment pressure
```

pero no:

```text
cow_purchase_recommended
```

---

## 3.5 No action encoding

SemanticState describe el estado y sus relaciones.

No debe decidir qué acción ejecutar.

```text
SemanticState
    ↓
"What is happening?"
```

El modelo de decisión responde:

```text
"What should I do?"
```

---

## 3.6 Preserve information

Cuando sea posible, las representaciones semánticas deben conservar la magnitud y el contexto de las señales originales.

Una representación booleana puede ser útil, pero no debería destruir innecesariamente la información cuantitativa.

---

# 4. Semantic Pattern Types

Los patrones pueden pertenecer a diferentes categorías.

| Tipo         | Significado                                                           |
| ------------ | --------------------------------------------------------------------- |
| State        | Describe una situación actual                                         |
| Event        | Describe un cambio o transición observable                            |
| Opportunity  | Describe una condición potencialmente favorable                       |
| Risk         | Describe una condición potencialmente desfavorable                    |
| Alarm        | Describe una situación que requiere atención                          |
| Pressure     | Describe una restricción o tensión                                    |
| Conflict     | Describe fuerzas o condiciones que entran en tensión                  |
| Synergy      | Describe varias condiciones que juntas forman una situación favorable |
| Relationship | Describe una relación cuantitativa o semántica entre señales          |

---

# 5. Financial Patterns

| Pattern ID | Señales                          | Dominios  | Tipo        | Significado                                                           |
| ---------- | -------------------------------- | --------- | ----------- | --------------------------------------------------------------------- |
| FIN001     | cash + liquidity_ratio           | Financial | State       | Situación actual de liquidez                                          |
| FIN002     | cash + days_remaining            | Financial | Risk        | Capacidad de mantener operaciones durante el horizonte restante       |
| FIN003     | liquidity_ratio + days_remaining | Financial | Risk        | Presión financiera considerando el tiempo disponible                  |
| FIN004     | cash + investments               | Financial | State       | Relación entre liquidez inmediata y capital comprometido              |
| FIN005     | liquidity_ratio + investments    | Financial | Risk        | Nivel de exposición de la liquidez frente a inversiones existentes    |
| FIN006     | low_liquidity + low_cash         | Financial | Alarm       | Restricción financiera inmediata                                      |
| FIN007     | high_liquidity + high_cash       | Financial | Opportunity | Capacidad financiera disponible                                       |
| FIN008     | liquidity_improving              | Financial | Event       | Recuperación de la posición financiera                                |
| FIN009     | liquidity_deteriorating          | Financial | Event       | Deterioro de la posición financiera                                   |
| FIN010     | low_liquidity + long_horizon     | Financial | Risk        | Recursos financieros insuficientes para un horizonte operativo amplio |
| FIN011     | high_liquidity + short_horizon   | Financial | State       | Recursos suficientes pero poco tiempo operativo restante              |
| FIN012     | cash + investment_capacity       | Financial | Opportunity | Capacidad potencial para realizar inversiones                         |

---

# 6. Agriculture Patterns

| Pattern ID | Señales                                | Dominios    | Tipo        | Significado                                                 |
| ---------- | -------------------------------------- | ----------- | ----------- | ----------------------------------------------------------- |
| AGR001     | production_ready                       | Agriculture | State       | Existe producción lista                                     |
| AGR002     | production_quantity + production_ready | Agriculture | State       | Magnitud de producción disponible                           |
| AGR003     | production_ready + free_land           | Agriculture | Opportunity | Producción disponible y capacidad de expansión              |
| AGR004     | production_ready + low_free_land       | Agriculture | Pressure    | Producción existente con poca capacidad agrícola disponible |
| AGR005     | production_increasing                  | Agriculture | Event       | Producción disponible en crecimiento                        |
| AGR006     | production_decreasing                  | Agriculture | Event       | Producción disponible en disminución                        |
| AGR007     | high_occupied_land + low_free_land     | Agriculture | Risk        | Capacidad agrícola cercana al límite                        |
| AGR008     | low_occupied_land + high_free_land     | Agriculture | Opportunity | Capacidad agrícola disponible                               |
| AGR009     | crop_age + production_ready            | Agriculture | State       | Producción madura o preparada según ciclo                   |
| AGR010     | production_ready + time_pressure       | Agriculture | Pressure    | Producción lista bajo restricciones temporales              |

---

# 7. Inventory / Storage Patterns

| Pattern ID | Señales                                    | Dominios  | Tipo        | Significado                                             |
| ---------- | ------------------------------------------ | --------- | ----------- | ------------------------------------------------------- |
| INV001     | shed_utilization                           | Inventory | State       | Nivel actual de utilización del almacenamiento          |
| INV002     | shed_utilization + shed_available          | Inventory | State       | Ocupación y capacidad restante                          |
| INV003     | high_shed_utilization + low_shed_available | Inventory | Risk        | Almacenamiento cercano a saturación                     |
| INV004     | low_shed_utilization + high_shed_available | Inventory | Opportunity | Capacidad de almacenamiento disponible                  |
| INV005     | inventory_increasing                       | Inventory | Event       | Acumulación de inventario                               |
| INV006     | inventory_decreasing                       | Inventory | Event       | Reducción de inventario                                 |
| INV007     | high_inventory + low_storage               | Inventory | Pressure    | Inventario elevado con poca capacidad restante          |
| INV008     | low_inventory + high_storage               | Inventory | Opportunity | Capacidad disponible con inventario reducido            |
| INV009     | product_concentration                      | Inventory | Risk        | Dependencia elevada de determinados productos           |
| INV010     | inventory_value + storage_utilization      | Inventory | State       | Valor económico almacenado frente a capacidad utilizada |

---

# 8. Market Patterns

| Pattern ID | Señales                                | Dominios | Tipo        | Significado                                          |
| ---------- | -------------------------------------- | -------- | ----------- | ---------------------------------------------------- |
| MKT001     | price                                  | Market   | State       | Nivel actual del precio                              |
| MKT002     | price_change_pct                       | Market   | Event       | Variación reciente del precio                        |
| MKT003     | price_trend                            | Market   | State       | Dirección del mercado                                |
| MKT004     | market_pressure                        | Market   | State       | Intensidad de presión del mercado                    |
| MKT005     | price + price_trend                    | Market   | Opportunity | Precio actual acompañado por una tendencia favorable |
| MKT006     | price + negative_trend                 | Market   | Risk        | Precio actual con deterioro de mercado               |
| MKT007     | positive_trend + positive_price_change | Market   | Event       | Mercado mejorando                                    |
| MKT008     | negative_trend + negative_price_change | Market   | Event       | Mercado deteriorándose                               |
| MKT009     | high_market_pressure + falling_price   | Market   | Risk        | Presión elevada acompañada por deterioro de precio   |
| MKT010     | low_market_pressure + rising_price     | Market   | Opportunity | Condiciones favorables de mercado                    |

---

# 9. Livestock Patterns

| Pattern ID | Señales                                   | Dominios  | Tipo  | Significado                                           |
| ---------- | ----------------------------------------- | --------- | ----- | ----------------------------------------------------- |
| LIV001     | total_animals                             | Livestock | State | Presencia y magnitud del ganado                       |
| LIV002     | placed_animals + shed_animals             | Livestock | State | Distribución del ganado entre granja y almacenamiento |
| LIV003     | animals_needing_attention                 | Livestock | Alarm | Animales que requieren atención                       |
| LIV004     | animals_needing_attention + time_pressure | Livestock | Risk  | Necesidades ganaderas bajo presión temporal           |
| LIV005     | animal_asset_value                        | Livestock | State | Valor económico del ganado                            |
| LIV006     | total_animals + animal_asset_value        | Livestock | State | Exposición económica al ganado                        |
| LIV007     | animals_increasing                        | Livestock | Event | Expansión del livestock                               |
| LIV008     | animals_decreasing                        | Livestock | Event | Reducción del livestock                               |

---

# 10. Agriculture × Inventory

| Pattern ID | Señales                               | Dominios                | Tipo         | Significado                                                  |
| ---------- | ------------------------------------- | ----------------------- | ------------ | ------------------------------------------------------------ |
| AI001      | production_ready + shed_available     | Agriculture + Inventory | Opportunity  | Producción lista con capacidad para almacenarla              |
| AI002      | production_ready + low_shed_available | Agriculture + Inventory | Risk         | Producción lista con capacidad de almacenamiento limitada    |
| AI003      | production_ready + storage_pressure   | Agriculture + Inventory | Pressure     | Producción ejerciendo presión sobre almacenamiento           |
| AI004      | production_quantity + shed_available  | Agriculture + Inventory | Relationship | Relación entre producción disponible y capacidad             |
| AI005      | production_quantity > shed_available  | Agriculture + Inventory | Conflict     | Producción potencialmente superior a la capacidad disponible |
| AI006      | production_ready + high_inventory     | Agriculture + Inventory | Pressure     | Producción nueva en un entorno ya cargado de inventario      |

---

# 11. Agriculture × Market

| Pattern ID | Señales                                   | Dominios             | Tipo         | Significado                                      |
| ---------- | ----------------------------------------- | -------------------- | ------------ | ------------------------------------------------ |
| AM001      | production_ready + price                  | Agriculture + Market | Opportunity  | Producción lista con precio de mercado relevante |
| AM002      | production_ready + rising_price           | Agriculture + Market | Opportunity  | Producción lista mientras el mercado mejora      |
| AM003      | production_ready + falling_price          | Agriculture + Market | Risk         | Producción lista mientras el mercado empeora     |
| AM004      | production_quantity + price               | Agriculture + Market | Relationship | Valor potencial de la producción según mercado   |
| AM005      | production_ready + price + positive_trend | Agriculture + Market | Opportunity  | Producción lista en un mercado favorable         |
| AM006      | production_ready + price + negative_trend | Agriculture + Market | Pressure     | Producción lista bajo deterioro del mercado      |
| AM007      | production_ready + market_pressure        | Agriculture + Market | Pressure     | Producción lista frente a presión de mercado     |

---

# 12. Inventory × Market

| Pattern ID | Señales                        | Dominios           | Tipo         | Significado                                         |
| ---------- | ------------------------------ | ------------------ | ------------ | --------------------------------------------------- |
| IM001      | inventory + price              | Inventory + Market | Relationship | Valor potencial del inventario según mercado        |
| IM002      | high_inventory + high_price    | Inventory + Market | Opportunity  | Stock elevado con valoración de mercado favorable   |
| IM003      | high_inventory + falling_price | Inventory + Market | Risk         | Inventario elevado mientras pierde valor            |
| IM004      | low_inventory + rising_price   | Inventory + Market | Opportunity  | Recursos escasos mientras mejora el mercado         |
| IM005      | inventory + price_trend        | Inventory + Market | Relationship | Exposición del inventario a la dinámica del mercado |
| IM006      | inventory + market_pressure    | Inventory + Market | Risk         | Inventario expuesto a presión de mercado            |

---

# 13. Financial × Inventory

| Pattern ID | Señales                                          | Dominios              | Tipo         | Significado                                             |
| ---------- | ------------------------------------------------ | --------------------- | ------------ | ------------------------------------------------------- |
| FI001      | low_liquidity + high_inventory                   | Financial + Inventory | Risk         | Capital inmovilizado en inventario                      |
| FI002      | low_liquidity + low_inventory                    | Financial + Inventory | Alarm        | Restricción financiera sin inventario significativo     |
| FI003      | high_liquidity + low_inventory                   | Financial + Inventory | Opportunity  | Capacidad financiera disponible con inventario reducido |
| FI004      | high_liquidity + high_inventory                  | Financial + Inventory | State        | Buena capacidad financiera y stock elevado              |
| FI005      | inventory_value + cash                           | Financial + Inventory | Relationship | Relación entre liquidez e inventario valorizado         |
| FI006      | low_liquidity + high_inventory + inventory_value | Financial + Inventory | Pressure     | Elevada exposición económica con poca liquidez          |

---

# 14. Financial × Market

| Pattern ID | Señales                          | Dominios           | Tipo         | Significado                                          |
| ---------- | -------------------------------- | ------------------ | ------------ | ---------------------------------------------------- |
| FM001      | cash + price                     | Financial + Market | State        | Capacidad financiera frente a precios actuales       |
| FM002      | liquidity + favorable_market     | Financial + Market | Opportunity  | Capacidad financiera ante condiciones favorables     |
| FM003      | low_liquidity + favorable_market | Financial + Market | Conflict     | Oportunidad de mercado limitada por liquidez         |
| FM004      | high_liquidity + rising_price    | Financial + Market | Opportunity  | Capacidad financiera durante mercado creciente       |
| FM005      | low_liquidity + falling_price    | Financial + Market | Risk         | Restricción financiera durante deterioro del mercado |
| FM006      | cash + market_pressure           | Financial + Market | Relationship | Capacidad financiera frente a presión de mercado     |

---

# 15. Financial × Agriculture

| Pattern ID | Señales                           | Dominios                | Tipo        | Significado                                              |
| ---------- | --------------------------------- | ----------------------- | ----------- | -------------------------------------------------------- |
| FA001      | cash + production_ready           | Financial + Agriculture | State       | Liquidez frente a producción disponible                  |
| FA002      | low_liquidity + production_ready  | Financial + Agriculture | Pressure    | Producción disponible con recursos financieros limitados |
| FA003      | high_liquidity + production_ready | Financial + Agriculture | Opportunity | Producción disponible con capacidad financiera           |
| FA004      | low_liquidity + high_production   | Financial + Agriculture | Risk        | Alta producción con poca liquidez                        |
| FA005      | cash + free_land                  | Financial + Agriculture | Opportunity | Capacidad financiera y capacidad agrícola                |
| FA006      | low_liquidity + low_free_land     | Financial + Agriculture | Constraint  | Restricciones financieras y físicas simultáneas          |

---

# 16. Financial × Livestock

| Pattern ID | Señales                             | Dominios              | Tipo         | Significado                                       |
| ---------- | ----------------------------------- | --------------------- | ------------ | ------------------------------------------------- |
| FL001      | total_animals + cash                | Financial + Livestock | State        | Magnitud del livestock frente a liquidez          |
| FL002      | animal_asset_value + cash           | Financial + Livestock | Relationship | Valor ganadero frente a liquidez                  |
| FL003      | low_liquidity + high_animal_value   | Financial + Livestock | Risk         | Alta exposición ganadera con baja liquidez        |
| FL004      | high_liquidity + low_animal_value   | Financial + Livestock | Opportunity  | Capacidad financiera con baja exposición ganadera |
| FL005      | livestock_attention + low_liquidity | Financial + Livestock | Pressure     | Necesidades ganaderas con recursos limitados      |

---

# 17. Inventory × Livestock

| Pattern ID | Señales                                         | Dominios              | Tipo        | Significado                                                    |
| ---------- | ----------------------------------------------- | --------------------- | ----------- | -------------------------------------------------------------- |
| IL001      | placed_animals + shed_available                 | Inventory + Livestock | State       | Situación física del ganado y almacenamiento                   |
| IL002      | shed_animals + shed_utilization                 | Inventory + Livestock | Pressure    | Ganado almacenado dentro de un sistema con capacidad limitada  |
| IL003      | animals_in_inventory + storage_pressure         | Inventory + Livestock | Risk        | Recursos ganaderos compitiendo con capacidad de almacenamiento |
| IL004      | animals_needing_attention + inventory_available | Inventory + Livestock | Opportunity | Recursos disponibles para responder a necesidades ganaderas    |

---

# 18. Agriculture × Inventory × Market

| Pattern ID | Señales                                                | Dominios                         | Tipo        | Significado                                                                |
| ---------- | ------------------------------------------------------ | -------------------------------- | ----------- | -------------------------------------------------------------------------- |
| AIM001     | production_ready + shed_available + favorable_market   | Agriculture + Inventory + Market | Synergy     | Producción lista, capacidad disponible y mercado favorable                 |
| AIM002     | production_ready + storage_pressure + favorable_market | Agriculture + Inventory + Market | Conflict    | Producción y mercado favorables limitados por almacenamiento               |
| AIM003     | production_ready + storage_pressure + falling_price    | Agriculture + Inventory + Market | Risk        | Producción lista, almacenamiento limitado y mercado deteriorándose         |
| AIM004     | high_inventory + low_storage + falling_price           | Agriculture + Inventory + Market | Risk        | Acumulación física con pérdida de valor                                    |
| AIM005     | low_inventory + high_storage + rising_price            | Agriculture + Inventory + Market | Opportunity | Poco stock, capacidad disponible y mercado favorable                       |
| AIM006     | production_ready + high_price + positive_trend         | Agriculture + Inventory + Market | Opportunity | Condiciones de mercado especialmente favorables para producción disponible |

---

# 19. Financial × Inventory × Market

| Pattern ID | Señales                                        | Dominios                       | Tipo        | Significado                                                            |
| ---------- | ---------------------------------------------- | ------------------------------ | ----------- | ---------------------------------------------------------------------- |
| FIM001     | low_liquidity + high_inventory + high_price    | Financial + Inventory + Market | Opportunity | Inventario valioso que puede representar capacidad de generar liquidez |
| FIM002     | low_liquidity + high_inventory + falling_price | Financial + Inventory + Market | Risk        | Baja liquidez y stock perdiendo valor                                  |
| FIM003     | high_liquidity + low_inventory + rising_price  | Financial + Inventory + Market | Opportunity | Capacidad financiera frente a mercado favorable                        |
| FIM004     | high_liquidity + high_inventory + high_price   | Financial + Inventory + Market | State       | Posición económica fuerte con activos almacenados                      |
| FIM005     | low_liquidity + low_inventory + rising_price   | Financial + Inventory + Market | Conflict    | Mercado favorable pero capacidad financiera limitada                   |

---

# 20. Financial × Agriculture × Market

| Pattern ID | Señales                                          | Dominios                         | Tipo        | Significado                                                                 |
| ---------- | ------------------------------------------------ | -------------------------------- | ----------- | --------------------------------------------------------------------------- |
| FAM001     | production_ready + high_price + high_liquidity   | Financial + Agriculture + Market | Synergy     | Producción disponible, mercado favorable y capacidad financiera             |
| FAM002     | production_ready + high_price + low_liquidity    | Financial + Agriculture + Market | Conflict    | Oportunidad productiva/mercado limitada por liquidez                        |
| FAM003     | production_ready + falling_price + low_liquidity | Financial + Agriculture + Market | Risk        | Producción disponible durante deterioro de mercado y restricción financiera |
| FAM004     | production_ready + rising_price + high_liquidity | Financial + Agriculture + Market | Opportunity | Situación favorable para actividad económica/productiva                     |
| FAM005     | low_liquidity + free_land + favorable_market     | Financial + Agriculture + Market | Opportunity | Capacidad física y mercado favorable con restricción financiera             |

---

# 21. Financial × Agriculture × Inventory

| Pattern ID | Señales                                               | Dominios                            | Tipo        | Significado                                                    |
| ---------- | ----------------------------------------------------- | ----------------------------------- | ----------- | -------------------------------------------------------------- |
| FAI001     | low_liquidity + production_ready + storage_available  | Financial + Agriculture + Inventory | Opportunity | Producción disponible y almacenamiento, pero liquidez limitada |
| FAI002     | low_liquidity + production_ready + storage_pressure   | Financial + Agriculture + Inventory | Risk        | Restricción financiera y física simultánea                     |
| FAI003     | high_liquidity + production_ready + storage_available | Financial + Agriculture + Inventory | Synergy     | Capacidad financiera, productiva y física                      |
| FAI004     | high_inventory + production_ready + low_liquidity     | Financial + Agriculture + Inventory | Pressure    | Acumulación productiva con presión financiera                  |
| FAI005     | production_ready + high_inventory + storage_pressure  | Agriculture + Inventory + Financial | Risk        | Producción e inventario acumulados con capacidad limitada      |

---

# 22. Livestock × Financial × Inventory

| Pattern ID | Señales                                                         | Dominios                          | Tipo        | Significado                                                        |
| ---------- | --------------------------------------------------------------- | --------------------------------- | ----------- | ------------------------------------------------------------------ |
| LFI001     | high_animal_value + low_liquidity                               | Livestock + Financial             | Risk        | Elevada exposición económica al ganado con poca liquidez           |
| LFI002     | livestock_attention + low_liquidity + low_inventory             | Livestock + Financial + Inventory | Alarm       | Necesidades ganaderas con recursos financieros y físicos limitados |
| LFI003     | livestock_attention + inventory_available + liquidity_available | Livestock + Financial + Inventory | Opportunity | Capacidad para responder a necesidades ganaderas                   |
| LFI004     | high_animal_value + high_liquidity                              | Livestock + Financial             | State       | Exposición ganadera respaldada por liquidez                        |
| LFI005     | animals_needing_attention + time_pressure + low_liquidity       | Livestock + Financial             | Risk        | Necesidad ganadera urgente bajo restricción financiera             |

---

# 23. High-Composition Patterns

Estos patrones combinan señales procedentes de varios dominios simultáneamente.

| Pattern ID | Señales                                                                        | Dominios                                        | Tipo        | Significado                                                                            |
| ---------- | ------------------------------------------------------------------------------ | ----------------------------------------------- | ----------- | -------------------------------------------------------------------------------------- |
| SEM001     | production_ready + storage_available + favorable_market + sufficient_liquidity | Agriculture + Inventory + Market + Financial    | Synergy     | Producción lista, capacidad física, mercado favorable y respaldo financiero            |
| SEM002     | production_ready + storage_pressure + favorable_market + low_liquidity         | Agriculture + Inventory + Market + Financial    | Conflict    | Gran oportunidad potencial bloqueada por restricciones financieras y de almacenamiento |
| SEM003     | high_inventory + storage_pressure + falling_price + low_liquidity              | Inventory + Market + Financial                  | Alarm       | Inventario elevado, almacenamiento limitado, pérdida de valor y baja liquidez          |
| SEM004     | low_inventory + high_storage + rising_price + high_liquidity                   | Inventory + Market + Financial                  | Opportunity | Capacidad financiera y física disponibles ante mercado favorable                       |
| SEM005     | livestock_attention + low_liquidity + low_inventory + time_pressure            | Livestock + Financial + Inventory               | Alarm       | Necesidad operativa urgente con recursos limitados                                     |
| SEM006     | production_ready + high_price + positive_trend + available_storage             | Agriculture + Market + Inventory                | Opportunity | Condiciones altamente favorables para producción disponible                            |
| SEM007     | production_ready + falling_price + storage_pressure + low_liquidity            | Agriculture + Market + Inventory + Financial    | Risk        | Situación productiva comprometida por mercado, almacenamiento y liquidez               |
| SEM008     | high_liquidity + available_storage + favorable_market + free_land              | Financial + Inventory + Market + Agriculture    | Opportunity | Alta capacidad para aprovechar oportunidades productivas/económicas                    |
| SEM009     | high_inventory + high_animal_value + low_liquidity                             | Inventory + Livestock + Financial               | Risk        | Elevada exposición patrimonial con poca liquidez                                       |
| SEM010     | production_ready + livestock_attention + storage_pressure + low_liquidity      | Agriculture + Livestock + Inventory + Financial | Alarm       | Presión simultánea sobre producción, ganado, almacenamiento y liquidez                 |
| SEM011     | production_ready + favorable_market + storage_pressure                         | Agriculture + Market + Inventory                | Conflict    | Mercado atractivo pero capacidad física limitada                                       |
| SEM012     | production_ready + favorable_market + low_liquidity                            | Agriculture + Market + Financial                | Conflict    | Oportunidad productiva/mercado limitada por liquidez                                   |
| SEM013     | favorable_market + high_liquidity + low_inventory                              | Market + Financial + Inventory                  | Opportunity | Capacidad económica disponible para aprovechar el mercado                              |
| SEM014     | unfavorable_market + high_inventory + high_storage                             | Market + Inventory                              | Risk        | Inventario elevado expuesto a un mercado desfavorable                                  |
| SEM015     | livestock_attention + sufficient_liquidity + available_inventory               | Livestock + Financial + Inventory               | Opportunity | Capacidad suficiente para atender necesidades del ganado                               |
| SEM016     | time_pressure + production_ready + favorable_market                            | Agriculture + Market + Financial                | Pressure    | Producción lista y mercado favorable bajo restricción temporal                         |
| SEM017     | time_pressure + livestock_attention + production_ready                         | Livestock + Agriculture                         | Alarm       | Presión temporal simultánea sobre producción y ganado                                  |
| SEM018     | liquidity_deteriorating + inventory_increasing + price_falling                 | Financial + Inventory + Market                  | Risk        | Tres tendencias negativas simultáneas                                                  |
| SEM019     | liquidity_improving + inventory_decreasing + price_rising                      | Financial + Inventory + Market                  | Synergy     | Evolución simultáneamente favorable de liquidez, inventario y mercado                  |
| SEM020     | production_increasing + storage_increasing + price_falling                     | Agriculture + Inventory + Market                | Risk        | Producción acumulándose mientras el mercado pierde valor                               |

---

# 24. Candidate Pattern Validation

La presencia de un patrón en este documento **no significa que deba implementarse**.

Cada candidato debe pasar por una validación posterior.

```text
PATTERN
   ↓
¿Las señales existen?
   ↓
¿Los getters son reales?
   ↓
¿La regla puede definirse determinísticamente?
   ↓
¿Tiene significado empresarial?
   ↓
¿Aporta información adicional?
   ↓
¿Es redundante?
   ↓
¿Existe target leakage?
   ↓
ACCEPT / MODIFY / REJECT
```

---

# 25. Relationship Between Pattern Space and SemanticState

El `Semantic Pattern Space` representa el espacio de hipótesis.

`SemanticState` representa solamente los patrones que han sido validados y seleccionados para implementación.

```text
Semantic Pattern Space
        │
        │  exploration
        ↓
Candidate Patterns
        │
        │  validation
        ↓
Validated Patterns
        │
        │  implementation
        ↓
SemanticState
```

Por lo tanto:

```text
Pattern Space ≠ SemanticState
```

El Pattern Space puede ser mucho más grande.

---

# 26. Relationship With Machine Learning

SemanticState no debe aprender directamente las decisiones.

Su función es producir una representación semántica rica:

```text
DOMAIN FACTS
      ↓
SEMANTIC FEATURES
      ↓
SEMANTIC PATTERNS
      ↓
MODEL-SPECIFIC FEATURES
      ↓
MODEL
```

Por ejemplo, para un modelo cuyo target sea:

```text
BUY_COW
```

el modelo puede recibir información como:

```text
cash
liquidity_ratio
livestock_present
animal_asset_value
investment_pressure
market_state
time_pressure
financial_livestock_relationship
```

pero SemanticState no debe producir:

```text
buy_cow_recommended
```

porque eso convertiría la interpretación semántica en una decisión y podría introducir target leakage.

---

# 27. Future Extensions

El Pattern Space podrá ampliarse posteriormente con:

* eventos temporales;
* cambios de tendencia;
* aceleraciones;
* persistencia de situaciones;
* patrones de transición;
* secuencias de estados;
* relaciones entre decisiones anteriores y estados posteriores;
* patrones específicos de producción;
* patrones específicos de adquisición;
* patrones específicos de venta;
* patrones relacionados con workers;
* patrones relacionados con operaciones;
* patrones derivados de nuevos Business Experts.

Estas extensiones deberán respetar los mismos principios de validación.

---

# 28. Implementation Rule

**Ningún patrón se implementa únicamente porque aparezca en este documento.**

Antes de convertirse en una feature de `SemanticState`, debe verificarse:

1. Fuente de datos.
2. Business Expert responsable.
3. Getter real.
4. Regla determinista.
5. Significado empresarial.
6. Información conservada.
7. Utilidad para ML.
8. Ausencia de target leakage.
9. Ausencia de redundancia innecesaria.

El `Semantic Pattern Space` es, por tanto, el **mapa conceptual del espacio semántico del negocio** sobre el cual se construirá posteriormente `SemanticState`.
