# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-04

### Added
- **Core Dataset Integration:**
  - Integrated 13,588 source food records from USDA SR Legacy, FNDDS, and Foundation Foods archives.
  - Normalized 37,025 portion records with positive gram weights.
  - Added 1,012,333 nutrient observations in `nutrients_long.csv`.
  - Generated 163,056 linear quantity scaling examples (`quantity_examples.csv`).
- **Splits & Quality Assurance:**
  - Created zero-leakage `train.jsonl` (10,738), `validation.jsonl` (1,417), and `test.jsonl` (1,433) datasets grouped by normalized food name and NDB ID.
  - Included raw quality audit log (`quality_events.csv`).
- **Tooling & ML:**
  - Added stdlib-only search and quantity calculator CLI (`scripts/query.py`).
  - Added linear portion scaling module (`scripts/nutrition.py`).
  - Included TF-IDF + Ridge regression ML baseline (`scripts/train_baseline.py`, `scripts/predict.py`).
  - Added test suite with 100% passing tests (`tests/test_nutrition.py`).
- **Documentation & Metadata:**
  - Standardized root `LICENSE` (CC0-1.0 + MIT), `COPYRIGHT.md`, `CITATION.cff`, `DATASET_CARD.md`, and `SOURCES.md`.
