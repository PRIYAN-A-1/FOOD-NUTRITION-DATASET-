"""Deterministic nutrition calculations. No ML needed for portion scaling."""
import math

NUTRIENTS = ['energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fiber_g',
             'sugars_g', 'saturated_fat_g', 'sodium_mg', 'cholesterol_mg',
             'calcium_mg', 'iron_mg', 'potassium_mg', 'vitamin_c_mg', 'water_g']


def number(value, name='quantity'):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and non-negative')
    return value


def scale(food, grams):
    """food has per-100g keys; unknown stays None, including a zero portion."""
    grams = number(grams)
    return {key: None if food.get(key + '_100g') in (None, '') else
            round(float(food[key + '_100g']) * grams / 100, 6)
            for key in NUTRIENTS}


def portion_grams(portion, count=1):
    """Count means multiples of the ENTIRE source-described portion.

    If the portion describes '2 tbsp, 33.9g', count=1 means 33.9g,
    count=.5 means 1 tbsp=16.95g. Never assume a generic cup/piece weight.
    """
    weight = number(portion['gram_weight'], 'portion gram weight')
    if weight <= 0:
        raise ValueError('Source portion has no usable gram weight')
    return number(count) * weight


def volume_grams(ml, density_g_ml):
    """Caller must supply a validated food-specific density."""
    density = number(density_g_ml, 'density')
    if density <= 0:
        raise ValueError('Density must be greater than zero')
    return number(ml) * density


def recipe(items, cooked_yield_g=None):
    """items = [(food_record, edible_grams), ...]. No retention assumptions.

    Added cooking oil must be an ingredient. This is ingredient-sum nutrition;
    cooking losses/retention require separately validated data. If any ingredient
    lacks a nutrient, the total for that nutrient stays unknown.
    """
    if not items:
        raise ValueError('At least one ingredient is required')
    scaled = [scale(food, grams) for food, grams in items]
    total = {k: None if any(row[k] is None for row in scaled) else
             round(sum(row[k] for row in scaled), 6) for k in NUTRIENTS}
    result = {'total': total, 'method': 'ingredient_sum_without_retention_adjustment'}
    if cooked_yield_g is not None:
        weight = number(cooked_yield_g, 'cooked yield')
        if weight <= 0:
            raise ValueError('Cooked yield must be greater than zero')
        result['per_100g'] = {k: None if v is None else round(v * 100 / weight, 6)
                              for k, v in total.items()}
    return result
