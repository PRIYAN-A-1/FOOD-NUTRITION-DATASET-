"""Search source records and calculate exact scaled source nutrition. Stdlib only."""
import argparse
import json
from pathlib import Path
from nutrition import scale, portion_grams
import csv

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--search', help='Case-insensitive literal name search; does not guess food')
    p.add_argument('--food-id',help='Exact source id, e.g. usda:2707894')
    group=p.add_mutually_exclusive_group()
    group.add_argument('--grams',type=float,default=None)
    group.add_argument('--portion-id',help='Exact portion id from portions.csv')
    p.add_argument('--count',type=float,default=1,help='Multiples of entire source-described portion')
    args=p.parse_args()
    if not args.search and not args.food_id:p.error('Use --search or --food-id')
    foods=[json.loads(line) for line in (ROOT/'data/foods.jsonl').open(encoding='utf-8')]
    if args.food_id:
        found=[f for f in foods if f['food_id']==args.food_id]
        if not found:p.error('Unknown food id')
        food=found[0]
        if args.portion_id:
            with (ROOT/'data/portions.csv').open(encoding='utf-8') as f:
                portions=[r for r in csv.DictReader(f) if r['portion_id']==args.portion_id and r['food_id']==args.food_id]
            if not portions:p.error('Portion not found for selected food')
            grams=portion_grams(portions[0],args.count)
        else:grams=args.grams if args.grams is not None else 100
        print(json.dumps({'food_id':food['food_id'],'name':food['name'],'quantity_g':grams,
                          'nutrition':scale(food,grams),'source_url':food['source_url'],
                          'method':'scaled_source_values_not_model_prediction'},indent=2,ensure_ascii=False))
    else:
        found=[{'food_id':f['food_id'],'name':f['name'],'source_type':f['source_type']} for f in foods if args.search.casefold() in f['name'].casefold()]
        print(json.dumps(found[:30],indent=2,ensure_ascii=False))
        print(f'{len(found)} matches; displaying up to 30. Use an exact food id for calculation.')

if __name__=='__main__':main()
