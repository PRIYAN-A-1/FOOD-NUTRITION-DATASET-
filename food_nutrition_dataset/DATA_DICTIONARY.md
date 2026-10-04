# Data dictionary

All text is UTF-8. CSV blanks mean unknown/missing, never zero. JSONL uses null for unknown values. IDs are strings. The 100 g basis is the edible portion in the preparation state described by the source, not necessarily as purchased.

## foods.csv / foods.jsonl / train.jsonl / validation.jsonl / test.jsonl

One row per USDA food record, NOT one row per universally unique food. Distinct preparation states, brands and source types remain separate. Names and category labels are verbatim source text. Country of origin is unknown and is not inferred from a dish name.

| Field | Meaning |
|---|---|
| food_id | Namespaced key `usda:FDC_ID` |
| fdc_id | Original USDA record identifier |
| name | Original full description, including raw/cooked details where provided |
| source_type | SR Legacy, Survey (FNDDS), Foundation |
| category / category_scheme | Source category and its taxonomy; WWEIA and USDA categories are not harmonized |
| ndb_number / food_code | Source identifiers, if available |
| source_release / publication_date | Archive release and original record publication date; publication date is preserved as source text |
| basis_amount / basis_unit | 100 / g |
| edible_portion_basis | True; user must provide edible grams matching the source state |
| source_url | Exact source record link |
| footnote | Source caveat when supplied |
| country_of_origin | Null, not established by these records |
| energy_kcal_100g | Selected source energy, kcal per 100 g |
| protein_g_100g / fat_g_100g / carbohydrate_g_100g | Source macros, grams per 100 g; carbohydrate by difference |
| fiber_g_100g / sugars_g_100g / saturated_fat_g_100g / water_g_100g | Grams per 100 g |
| sodium_mg_100g / cholesterol_mg_100g / calcium_mg_100g / iron_mg_100g / potassium_mg_100g / vitamin_c_mg_100g | Milligrams per 100 g |
| nutrient_ids_json | Exact nutrient IDs selected into each wide column |
| missing_nutrients | Pipe-separated missing wide-column nutrients |
| complete_core_macros | Energy, protein, fat and carbohydrate are all available |
| split_group / split | Group identifier and deterministic train/validation/test assignment |

Energy selection: nutrient 1008 when present, otherwise 2048 (Atwater specific), then 2047 (Atwater general). This is a transparent convenience policy, not a claim those methods are equivalent. All source energy values remain in nutrients_long.csv. Sugars use 2000 if present, otherwise 1063; definitions remain visible in the long table. We do not invent energy from a 4-4-9 calculation when it is absent.

## portions.csv

One row per positive source gram-weight portion. `portion_id` joins to `food_id`. `description`, `source_amount`, `source_measure_unit`, `source_modifier` preserve source serving details. `gram_weight` applies to the ENTIRE described portion. `count=2` multiplies that complete portion by two. A source portion such as “2 tablespoons = 33.9 g” is not 33.9 g per tablespoon. FNDDS often encodes the amount in its description rather than a numeric amount field.

“Quantity not specified” records are survey default assumptions, not measured user portions. Do not choose them automatically. “1 item” depends on the source item's size. For real intake, weighing food is preferable to assuming all pieces have the same weight. A generic cup/ml conversion is not provided; use source-specific portions or a validated density.

## nutrients_long.csv

All source food-nutrient observations: food_id, fdc_id, source_food_nutrient_id, nutrient_id, nutrient_name, unit, amount_100g, derivation_code, derivation_description, data_points, min, max, median, loq. Units can be g, mg, µg, kcal, kJ, IU, etc. Never sum unlike units. LOQ means limit of quantification; preserve it when interpreting censored measurements. The table contains measured, calculated, manufacturer-supplied and imputed values as indicated by the source. It is not one million independent laboratory experiments. Original archives retain metadata not flattened here.

## quantity_examples.csv

One derived example per food and quantity in [5,10,25,50,75,100,125,150,200,250,300,500] g. Nutrients have the same units as their suffix, but represent the requested portion rather than 100 g. These are formula-generated labels, NOT new measured foods or independent training observations. Use the included split, never shuffle quantity rows into new random splits. The calculation function accepts arbitrary non-negative finite grams, not just these twelve quantities.

## Splits

Identical normalized names and shared NDB numbers are unioned into a group; hashing the group assigns approximately 80/10/10. Food variants/related recipes may still cross groups. These splits prevent direct duplicate-name and NDB leakage, but are not cuisine-held-out, household-held-out or unseen-recipe-family evaluations. Each source record remains in the dataset to preserve provenance.

## quality_events.csv

Records excluded due to null source entries or unusable portion weights. Missing nutrients are retained in foods, not removed. Only complete core records are used by the provided ML baseline.
