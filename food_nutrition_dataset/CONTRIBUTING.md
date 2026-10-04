# Contributing Guidelines

Thank you for your interest in contributing to the **Food Nutrition Dataset — Priyan Edition**!

We welcome contributions that improve dataset quality, add verified national/regional food composition records, enhance performance of calculation tools, or expand documentation.

---

## Contribution Workflow

### 1. Adding New Food Data
Before contributing new food composition records:
- **Source Verification:** Ensure data comes from an official national food-composition database or verified analytical lab assay.
- **Portion Basis:** Data must specify whether values are per 100 g edible portion or explicit portion weights.
- **No Zero Imputation:** Missing nutrient fields must be left blank (`None` / `null`) rather than assumed zero.
- **Preserve Source IDs:** Retain original database source IDs, release dates, and preparation descriptions.

### 2. Code Contributions
- Follow standard Python styling (PEP 8 compliant where feasible).
- Standard library dependencies (`stdlib`) are preferred for query and core calculation utilities.
- Add or update unit tests in `tests/` for any changes to calculations or data parsing.

### 3. Submitting Pull Requests
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-dataset-source`).
3. Run the test suite:
   ```powershell
   python -m unittest discover -s tests -v
   ```
4. Commit your changes with concise messages.
5. Open a Pull Request detailing the changes, data provenance, and test results.
