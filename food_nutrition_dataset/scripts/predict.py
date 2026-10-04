"""Optional experimental ML estimates. Prefer query.py for known foods."""
import argparse
import json
import sys
from pathlib import Path
from nutrition import number

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('name')
    p.add_argument('--grams', type=float, default=100)
    args = p.parse_args()
    grams = number(args.grams)
    model_path = ROOT / 'models/name_macro_baseline.joblib'
    if not model_path.exists():
        print(json.dumps({
            'error': 'Model file not found',
            'details': f'Missing {model_path}. Run `python scripts/train_baseline.py` first.'
        }, indent=2), file=sys.stderr)
        sys.exit(1)

    try:
        import joblib
        import numpy as np
        saved = joblib.load(model_path)
        values = np.maximum(0, saved['pipeline'].predict([args.name])[0])
        print(json.dumps({'name': args.name, 'quantity_g': grams, 'estimated': True,
            'method': 'experimental_name_regression_then_linear_scaling',
            'warning': 'Not verified food nutrition. Prefer an exact source record; model does not identify recipes or images.',
            'nutrition': {k.removesuffix('_100g'): round(float(v) * grams / 100, 3)
                         for k, v in zip(saved['targets'], values)}}, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': 'Failed to load or execute ML model',
            'details': str(e),
            'recommendation': 'Use scripts/query.py for exact food lookup, or run in Python 3.11+ with requirements-ml.txt.'
        }, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

