"""Rebuild all data files from the bundled original USDA JSON ZIPs. Stdlib only."""
import csv
import hashlib
import json
import math
import re
import zipfile
from collections import Counter
from pathlib import Path
from nutrition import NUTRIENTS, scale

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('sr', '2018-04', 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip'),
    ('fndds', '2024-10-31', 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_survey_food_json_2024-10-31.zip'),
    ('foundation', '2026-04-30', 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2026-04-30.zip'),
]
FIELDS = {
    'energy_kcal': [1008, 2048, 2047], 'protein_g': [1003], 'fat_g': [1004],
    'carbohydrate_g': [1005], 'fiber_g': [1079], 'sugars_g': [2000, 1063],
    'saturated_fat_g': [1258], 'sodium_mg': [1093], 'cholesterol_mg': [1253],
    'calcium_mg': [1087], 'iron_mg': [1089], 'potassium_mg': [1092],
    'vitamin_c_mg': [1162], 'water_g': [1051],
}
EXPECTED_UNITS = {k: ('kcal' if k == 'energy_kcal' else 'mg' if k.endswith('_mg') else 'g') for k in FIELDS}
GRAMS = [5, 10, 25, 50, 75, 100, 125, 150, 200, 250, 300, 500]


def dump_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def canonical(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def valid_amount(value):
    return isinstance(value, (float, int)) and math.isfinite(value) and value >= 0


def main():
    data_dir = ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    foods, portions, raw_refs, audits = [], [], [], []
    manifest, seen = [], set()
    nutrient_fields = ['food_id', 'fdc_id', 'source_food_nutrient_id', 'nutrient_id', 'nutrient_name',
                       'unit', 'amount_100g', 'derivation_code', 'derivation_description',
                       'data_points', 'min', 'max', 'median', 'loq']
    with (data_dir / 'nutrients_long.csv').open('w', newline='', encoding='utf-8') as nutrient_file:
        nw = csv.DictWriter(nutrient_file, fieldnames=nutrient_fields)
        nw.writeheader()
        nutrient_count = 0
        for source, release, url in SOURCES:
            path = ROOT / 'sources' / f'usda_{source}.zip'
            with zipfile.ZipFile(path) as z:
                raw = json.loads(z.read(next(n for n in z.namelist() if n.endswith('.json'))))
            records = next(iter(raw.values()))
            manifest.append({'source': source, 'release': release, 'download_url': url,
                             'retrieved_on': '2026-10-04', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'raw_array_entries': len(records), 'license': 'CC0-1.0'})
            for idx, r in enumerate(records):
                if not isinstance(r, dict):
                    audits.append({'source': source, 'record': idx, 'issue': 'null_or_non_object_record_skipped'})
                    continue
                fdc = r['fdcId']
                if fdc in seen:
                    raise ValueError(f'Duplicate FDC id: {fdc}')
                seen.add(fdc)
                fid = f'usda:{fdc}'
                nutrients = {}
                for n in r.get('foodNutrients', []):
                    meta = n.get('nutrient') or {}
                    nid = meta.get('id')
                    derivation = n.get('foodNutrientDerivation') or {}
                    amount = n.get('amount')
                    nw.writerow(dict(zip(nutrient_fields, [fid, fdc, n.get('id'), nid,
                        meta.get('name'), meta.get('unitName'), amount,
                        derivation.get('code'), derivation.get('description'), n.get('dataPoints'),
                        n.get('min'), n.get('max'), n.get('median'), n.get('loq')])))
                    nutrient_count += 1
                    if nid in nutrients:
                        audits.append({'source':source,'record':fdc,'issue':f'duplicate_nutrient_{nid}_first_retained'})
                    else:
                        nutrients[nid] = n
                category = (r.get('foodCategory') or {}).get('description')
                scheme = 'USDA foodCategory'
                if not category:
                    category = (r.get('wweiaFoodCategory') or {}).get('wweiaFoodCategoryDescription')
                    scheme = 'WWEIA food category' if category else None
                food = {'food_id': fid, 'fdc_id': fdc, 'name': r['description'],
                        'source_type': r['dataType'], 'category': category, 'category_scheme': scheme,
                        'ndb_number': r.get('ndbNumber'), 'food_code': r.get('foodCode'),
                        'source_release': release, 'publication_date': r.get('publicationDate'),
                        'basis_amount': 100, 'basis_unit': 'g', 'edible_portion_basis': True,
                        'source_url': f'https://fdc.nal.usda.gov/food-details/{fdc}/nutrients',
                        'footnote': r.get('footnote'), 'country_of_origin': None}
                chosen = {}
                for key, candidates in FIELDS.items():
                    found = None
                    for nid in candidates:
                        n = nutrients.get(nid)
                        if n and valid_amount(n.get('amount')) and n['nutrient']['unitName'].lower() == EXPECTED_UNITS[key]:
                            found = n
                            chosen[key] = nid
                            break
                    food[key + '_100g'] = found['amount'] if found else None
                food['nutrient_ids_json'] = json.dumps(chosen, sort_keys=True, separators=(',', ':'))
                food['missing_nutrients'] = '|'.join(k for k in NUTRIENTS if food[k+'_100g'] is None)
                food['complete_core_macros'] = all(food[k+'_100g'] is not None for k in NUTRIENTS[:4])
                foods.append(food)
                raw_refs.append((food, r))
                for j, p in enumerate(r.get('foodPortions', [])):
                    weight = p.get('gramWeight')
                    if not valid_amount(weight) or weight <= 0:
                        audits.append({'source':source,'record':fdc,'issue':'nonpositive_or_missing_portion_weight_excluded'})
                        continue
                    unit = (p.get('measureUnit') or {}).get('name')
                    amount = p.get('amount')
                    desc = p.get('portionDescription')
                    if not desc:
                        desc = ' '.join(str(v) for v in [amount,
                            unit if unit != 'undetermined' else None, p.get('modifier')] if v not in (None, ''))
                    portions.append({'portion_id': f'{fid}:portion:{p.get("id", j)}',
                                     'food_id':fid, 'source_portion_id':p.get('id'),
                                     'description':desc, 'source_amount':amount,
                                     'source_measure_unit':unit, 'source_modifier':p.get('modifier'),
                                     'gram_weight':weight, 'count_semantics':'multiples_of_entire_described_portion'})

    # Union identical normalized descriptions and shared NDB IDs across sources.
    parent = {f['food_id']:f['food_id'] for f in foods}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    keys = {}
    for food in foods:
        group_keys = ['name:'+canonical(food['name'])]
        if food['ndb_number'] is not None:
            group_keys.append('ndb:'+str(food['ndb_number']))
        for key in group_keys:
            if key in keys:
                a, b = sorted([find(food['food_id']), find(keys[key])])
                parent[b] = a
            else:
                keys[key] = food['food_id']
    for food in foods:
        food['split_group'] = find(food['food_id'])
        bucket = int(hashlib.sha256(food['split_group'].encode()).hexdigest()[:8],16) % 100
        food['split'] = 'train' if bucket < 80 else 'validation' if bucket < 90 else 'test'

    foods.sort(key=lambda f:f['fdc_id'])
    dump_csv(data_dir/'foods.csv', foods)
    dump_csv(data_dir/'portions.csv', portions)
    with (data_dir/'foods.jsonl').open('w',encoding='utf-8') as out:
        for f in foods: out.write(json.dumps(f,ensure_ascii=False)+'\n')
    for split in ['train','validation','test']:
        with (data_dir/f'{split}.jsonl').open('w',encoding='utf-8') as out:
            for f in foods:
                if f['split'] == split: out.write(json.dumps(f,ensure_ascii=False)+'\n')
    with (data_dir/'quantity_examples.csv').open('w',newline='',encoding='utf-8') as out:
        qfields=['food_id','split_group','split','quantity_g','label_method']+NUTRIENTS
        w=csv.DictWriter(out,fieldnames=qfields);w.writeheader()
        for f in foods:
            for g in GRAMS:
                w.writerow({'food_id':f['food_id'],'split_group':f['split_group'],'split':f['split'],
                            'quantity_g':g,'label_method':'derived_linear_scaling_not_independent_measurement',**scale(f,g)})

    # Check all selected wide values against source before declaring success.
    for f,r in raw_refs:
        chosen=json.loads(f['nutrient_ids_json'])
        for key,nid in chosen.items():
            source_value=next(n['amount'] for n in r['foodNutrients'] if n['nutrient']['id']==nid)
            assert f[key+'_100g']==source_value
    split_sets={s:{f['split_group'] for f in foods if f['split']==s} for s in ['train','validation','test']}
    assert not (split_sets['train']&split_sets['validation'] or split_sets['train']&split_sets['test'] or split_sets['validation']&split_sets['test'])
    counts={'food_records':len(foods),'distinct_normalized_names':len({canonical(f['name']) for f in foods}),
            'source_types':dict(Counter(f['source_type'] for f in foods)),
            'valid_source_portions':len(portions),'nutrient_observations':nutrient_count,
            'derived_quantity_examples':len(foods)*len(GRAMS),'quantity_grid_grams':GRAMS,
            'complete_core_macro_records':sum(f['complete_core_macros'] for f in foods),
            'missing_by_nutrient':{k:sum(f[k+'_100g'] is None for f in foods) for k in NUTRIENTS},
            'splits':dict(Counter(f['split'] for f in foods)),
            'quality_events':dict(Counter(a['issue'] for a in audits)),
            'validation':{'selected_nutrients_match_source':True,'no_split_group_overlap':True},
            'coverage':'USDA-centered; NOT all foods worldwide; origin/cuisine not inferred'}
    (ROOT/'DATA_REPORT.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
    (ROOT/'SOURCES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    dump_csv(data_dir/'quality_events.csv',audits,['source','record','issue'])
    print(json.dumps(counts,indent=2))

if __name__=='__main__': main()
