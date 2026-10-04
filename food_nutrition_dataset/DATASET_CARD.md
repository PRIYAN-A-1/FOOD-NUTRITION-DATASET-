# Dataset Card: Food Nutrition Dataset — Priyan Edition

## 1. Dataset Overview

- **Dataset Name:** Food Nutrition Dataset — Priyan Edition
- **Version:** v1.0.0
- **Creator / Maintainer:** Priyan A (<priyan1436ei@gmail.com>)
- **Release Date:** 2026-10-04
- **License:** CC0 1.0 Universal (Dataset) / MIT License (Code)

---

## 2. Dataset Description

A standardized, high-quality nutrition starter corpus containing **13,588 source food records**, **37,025 positive portion weight mappings**, **1,012,333 nutrient observations**, and **163,056 derived linear quantity examples**. Designed for nutrition tracking applications, recipe calculators, portion scaling engines, and machine learning research.

---

## 3. Dataset Summary Statistics

| Metric | Count |
|---|---:|
| Source Food Records | 13,588 |
| Distinct Normalized Descriptions | 13,389 |
| Complete Core Macro Records (kcal, protein, fat, carbs) | 13,535 |
| Source Portions with Positive Gram Weights | 37,025 |
| Source Nutrient Observations (Long format) | 1,012,333 |
| Derived Scaled Quantity Examples | 163,056 |
| Train Split Records | 10,738 |
| Validation Split Records | 1,417 |
| Test Split Records | 1,433 |

---

## 4. Key Data Fields

### Core Food Fields (`foods.csv` / `foods.jsonl`)

| Field Name | Type | Description |
|---|---|---|
| `food_id` | string | Unique primary key (e.g. `usda:2708346`) |
| `fdc_id` | integer | USDA FoodData Central FDC ID |
| `name` | string | Normalized English description of food item |
| `source_type` | string | Dataset source type (`SR Legacy`, `Survey (FNDDS)`, `Foundation`) |
| `category` | string | Food category description |
| `energy_kcal_100g` | float | Energy content per 100 g edible portion (kcal) |
| `protein_g_100g` | float | Protein content per 100 g edible portion (g) |
| `fat_g_100g` | float | Total lipid/fat content per 100 g edible portion (g) |
| `carbohydrate_g_100g` | float | Carbohydrate by difference per 100 g edible portion (g) |
| `complete_core_macros` | boolean | True if calories, protein, fat, and carbs are all present |
| `split_group` | string | Canonical group ID ensuring related records share the same split |
| `split` | string | Split assignment (`train`, `validation`, `test`) |

---

## 5. Data Collection & Provenance

Data was retrieved on **October 4, 2026** from official U.S. Department of Agriculture (USDA) FoodData Central release archives:
- **USDA SR Legacy (April 2018):** 7,793 records
- **USDA FNDDS 2021–2023 (Oct 31, 2024 archive):** 5,432 records
- **USDA Foundation Foods (April 30, 2026 archive):** 363 records

See [`SOURCES.md`](SOURCES.md) for full archive URLs and SHA-256 verification hashes.

---

## 6. Quality Control & Normalization

- **Zero-Imputation Policy:** Missing nutrient values remain explicit blanks (`None`/`null`). No automatic zero-imputation is applied to preserve data integrity.
- **Portion Weight Validation:** All portion entries were validated; non-positive or missing gram weights were excluded.
- **Split Leakage Prevention:** Split grouping merges records with identical normalized descriptions and shared NDB numbers, preventing data leakage across train, validation, and test splits.

---

## 7. Limitations & Usage Guidelines

- **US-Centered Corpus:** The dataset is based on USDA measurements and does not cover every global or regional dish.
- **Linear Quantity Disclaimer:** Quantity examples (`quantity_examples.csv`) represent linear mathematical scaling ($nut / 100 \times grams$) and not separate physical assays.
- **ML Baseline Warning:** The baseline regression model is an experimental tool; exact food lookup via [`scripts/query.py`](scripts/query.py) should always be preferred for nutritional tracking.

---

## 8. License & Attribution

- **Data:** CC0 1.0 Universal (Public Domain)
- **Code:** MIT License
- **Maintainer:** Priyan A (<priyan1436ei@gmail.com>)
