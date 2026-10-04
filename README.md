# Food Nutrition Dataset — Priyan Edition

[![License: CC0-1.0](https://img.shields.io/badge/Dataset%20License-CC0--1.0-blue.svg)](LICENSE)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(6%2F6)-brightgreen.svg)](tests/)

**Maintainer & Author:** Priyan A (<priyan1436ei@gmail.com>)  
**Version:** `1.0.0` | **Release Date:** October 4, 2026  

---

## 📌 Executive Summary

**Food Nutrition Dataset — Priyan Edition** is a standardized, production-grade nutrition starter corpus and calculation toolkit built on official U.S. Department of Agriculture (USDA) FoodData Central release archives. 

It provides **13,588 source food records**, **37,025 portion gram mappings**, **1,012,333 nutrient observations**, **163,056 derived linear quantity examples**, zero-leakage ML splits (`train`, `validation`, `test`), a stdlib query CLI tool, and a baseline character-level regression model.

---

## 📊 Dataset Statistics & Overview

| Metric / Dimension | Count / Detail | Description |
|---|---:|---|
| **Total Source Food Records** | **13,588** | USDA SR Legacy, FNDDS, and Foundation foods |
| **Distinct Normalized Descriptions** | **13,389** | Unique standardized food names |
| **Complete Core Macro Records** | **13,535** | Records with energy, protein, fat, and carbs |
| **Valid Source Portion Weights** | **37,025** | Positive gram weight serving mappings |
| **Source Nutrient Observations** | **1,012,333** | Full long-format nutrient observation table |
| **Derived Quantity Examples** | **163,056** | Scaled linear quantities (5g to 500g grid) |
| **Train / Val / Test Splits** | **10,738 / 1,417 / 1,433** | Zero-leakage split grouping by normalized name & NDB ID |

---

## 📑 Repository Structure & Documentation

```text
food_nutrition_dataset/
├── README.md               ⭐ Main repository documentation & quickstart
├── LICENSE                 🔐 Root dual-license file (CC0 1.0 Data + MIT Code)
├── COPYRIGHT.md            ©️ Copyright notice & maintainer attribution
├── CITATION.cff            📚 Machine-readable GitHub citation file
├── DATASET_CARD.md         📊 Detailed dataset card, field schemas & quality docs
├── SOURCES.md              🔎 Raw dataset sources, URLs & SHA-256 hashes
├── CHANGELOG.md            🔄 Version release notes (Keep a Changelog standard)
├── CONTRIBUTING.md         🤝 Contribution & data submission guidelines
├── CODE_OF_CONDUCT.md      🛡️ Community pledge & enforcement standards
├── DATA_DICTIONARY.md      📖 Data field definitions, units & split policies
├── DATA_REPORT.json        📋 Automated counts, missingness & validation report
├── MODEL_REPORT.json       🤖 ML model architecture & evaluation metrics
├── SOURCES.json            📄 Raw JSON source manifest with SHA-256 hashes
├── VALIDATION.txt          ✅ Automated sanity check summary log
│
├── data/
│   ├── foods.csv           📦 Foods profile table (CSV format)
│   ├── foods.jsonl         📦 Foods profile records (JSONL format)
│   ├── portions.csv        ⚖️ Portion description & gram weight mapping
│   ├── nutrients_long.csv  🔬 Long nutrient observation table (1M+ rows)
│   ├── quantity_examples.csv 📏 Scaled linear quantity examples (163k+ rows)
│   ├── train.jsonl         🏋️ Training split records (10,738 records)
│   ├── validation.jsonl    🧪 Validation split records (1,417 records)
│   ├── test.jsonl          🎯 Test split records (1,433 records)
│   ├── quality_events.csv  🚨 Data cleaning audit log
│   └── schema.json         🧩 JSON schema definition for dataset validation
│
├── scripts/
│   ├── query.py            🔍 Stdlib search & exact portion scaling CLI
│   ├── nutrition.py        🧮 Pure deterministic nutrition math engine
│   ├── train_baseline.py   🏋️ TF-IDF + Ridge regression trainer
│   ├── predict.py          🤖 Experimental name-to-macros predictor CLI
│   └── build_dataset.py    🏗️ Reproducible dataset builder from raw ZIPs
│
├── tests/
│   └── test_nutrition.py   ✅ Unit tests for nutrition scaling engine
│
├── models/
│   └── name_macro_baseline.joblib 📦 Pre-trained ML baseline model
│
└── sources/                📦 Bundled USDA JSON source ZIP archives
```

---

## ⚡ Quickstart & Usage

### 1. Zero-Dependency Search & Quantity Calculation

No external machine learning packages are required for standard food lookup and portion scaling. Python 3.10+ stdlib is all you need:

```powershell
# Search food database by name (literal English match, max 30 matches)
python scripts/query.py --search "idli"

# Calculate exact nutrients for 150g edible portion
python scripts/query.py --food-id usda:2708346 --grams 150

# Calculate nutrients for 2 multiples of a specific source portion
python scripts/query.py --food-id usda:2708346 --portion-id usda:2708346:portion:302639 --count 2

# Run unit tests
python -m unittest discover -s tests -v
```

---

### 2. Experimental ML Baseline (Name-to-Macros Regression)

To train or run predictions with the included character TF-IDF + Ridge regression baseline model:

```powershell
# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements-ml.txt

# Train baseline model & generate MODEL_REPORT.json
python scripts/train_baseline.py

# Predict estimated nutrients for a food name (e.g. 150g vegetable curry)
python scripts/predict.py "vegetable curry" --grams 150
```

> **Warning:** ML estimations carry a held-out test MAE of **55.4 kcal/100g**, **2.92g protein/100g**, **4.70g fat/100g**, and **7.45g carbs/100g**. Always prefer exact source lookup via `query.py` over ML estimation for nutritional tracking.

---

### 3. Rebuild Dataset from Bundled USDA Source Archives

To deterministically rebuild all CSV, JSONL, and split files from raw USDA ZIP archives:

```powershell
python scripts/build_dataset.py
```

The builder verifies every wide-column nutrient against raw source JSON arrays, enforces missingness preservation (no automatic zero imputation), and ensures zero split-group leakage.

---

## 🧮 Nutrition Calculation & Quantity Scaling

Nutrient values scale linearly with edible portion weight:

$$\text{Portion Nutrient} = \frac{\text{Nutrient per } 100\text{g} \times \text{Edible Grams}}{100}$$

### Example: Idli (`usda:2708346`)

| Edible Amount | Calories (kcal) | Protein (g) | Fat (g) | Carbohydrates (g) |
|---:|---:|---:|---:|---:|
| **100 g** | 128.0 | 6.36 | 0.350 | 25.00 |
| **150 g** | 192.0 | 9.54 | 0.525 | 37.50 |
| **1 Piece (38 g)** | 48.64 | 2.4168 | 0.133 | 9.50 |

---

## 🌐 Dataset Provenance & Sources

All records originate from public domain releases of USDA FoodData Central:

| Source Name | Release Archive Date | Record Count | License |
|---|---|---:|---|
| **USDA SR Legacy** | April 2018 | 7,793 | CC0 1.0 Universal |
| **USDA FNDDS 2021–2023** | October 31, 2024 | 5,432 | CC0 1.0 Universal |
| **USDA Foundation Foods** | April 30, 2026 | 363 | CC0 1.0 Universal |

See [`SOURCES.md`](SOURCES.md) and [`SOURCES.json`](SOURCES.json) for raw archive links and SHA-256 verification hashes.

---

## 📜 Licensing & Attribution

This repository follows a dual-licensing structure:

- **Dataset & Derived Tables:** Dedicated to the Public Domain under [Creative Commons CC0 1.0 Universal](LICENSE).
- **Source Code & Scripts:** Licensed under the [MIT License](LICENSE).
- **Maintainer Attribution:** Copyright © 2026 **Priyan A** (<priyan1436ei@gmail.com>).

See [`COPYRIGHT.md`](COPYRIGHT.md) and [`LICENSE`](LICENSE) for full details.

---

## 📚 Citation

If you use this dataset or software in your research or applications, please cite it using [`CITATION.cff`](CITATION.cff):

```bibtex
@dataset{priyan2026foodnutrition,
  author       = {Priyan A},
  title        = {Food Nutrition Dataset — Priyan Edition},
  year         = {2026},
  version      = {1.0.0},
  publisher    = {GitHub},
  url          = {https://github.com/PRIYAN-A-1/food_nutrition_dataset}
}
```
