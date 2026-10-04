"""Optional name -> per-100g macro estimator. Exact food lookup is preferred.

This CPU baseline demonstrates real ML training; it is not an image model,
portion detector, medical model, or a replacement for measured nutrition.
"""
import json
from pathlib import Path
import numpy as np
import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT=Path(__file__).resolve().parents[1]
TARGETS=['energy_kcal_100g','protein_g_100g','fat_g_100g','carbohydrate_g_100g']

def load(split):
    rows=[json.loads(line) for line in (ROOT/'data'/f'{split}.jsonl').open(encoding='utf-8')]
    return [r for r in rows if r['complete_core_macros']]

def main():
    train,validation,test=(load(s) for s in ['train','validation','test'])
    y=np.array([[r[k] for k in TARGETS] for r in train])
    model=Pipeline([
        ('text',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=20000)),
        ('regressor',Ridge(alpha=3.0,solver='lsqr')),
    ])
    model.fit([r['name'] for r in train],y)
    report={'task':'food_name_to_per_100g_macros_experimental',
            'sklearn_version':sklearn.__version__,'training_records':len(train),
            'target_order':TARGETS,'prediction_policy':'clip negative predictions to zero',
            'split_policy':'identical normalized names and shared NDB ids grouped',
            'limitations':['USDA-centered evaluation, not worldwide performance',
                          'Related recipes can remain across splits',
                          'Not validated on user-entered names, Tamil or food images',
                          'Predictions are estimates; exact source lookup is preferred']}
    mean=y.mean(axis=0)
    for split,rows in [('validation',validation),('test',test)]:
        actual=np.array([[r[k] for k in TARGETS] for r in rows])
        predicted=np.maximum(0,model.predict([r['name'] for r in rows]))
        reference=np.tile(mean,(len(rows),1))
        report[split]={'records':len(rows),'metrics':{
            k:{'mae':float(mean_absolute_error(actual[:,i],predicted[:,i])),
               'rmse':float(np.sqrt(mean_squared_error(actual[:,i],predicted[:,i]))),
               'mean_predictor_mae':float(mean_absolute_error(actual[:,i],reference[:,i]))}
            for i,k in enumerate(TARGETS)}}
    model_dir=ROOT/'models';model_dir.mkdir(exist_ok=True)
    joblib.dump({'pipeline':model,'targets':TARGETS,'sklearn_version':sklearn.__version__},model_dir/'name_macro_baseline.joblib',compress=3)
    (ROOT/'MODEL_REPORT.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
