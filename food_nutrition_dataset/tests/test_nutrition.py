import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nutrition import scale,portion_grams,volume_grams,recipe

class NutritionTests(unittest.TestCase):
    def test_linear_portions(self):
        f={'energy_kcal_100g':130,'protein_g_100g':2.7}
        self.assertEqual(scale(f,250)['energy_kcal'],325)
        self.assertEqual(scale(f,250)['protein_g'],6.75)
        self.assertEqual(scale(f,0)['energy_kcal'],0)
        self.assertIsNone(scale(f,100)['fat_g'])
    def test_missing_does_not_become_zero(self):
        self.assertIsNone(scale({'fat_g_100g':''},0)['fat_g'])
    def test_invalid_quantity(self):
        for q in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):scale({},q)
    def test_portion_means_whole_description(self):
        self.assertEqual(portion_grams({'gram_weight':33.9},2),67.8)
        with self.assertRaises(ValueError):portion_grams({'gram_weight':0})
    def test_volume_density_required(self):
        self.assertEqual(volume_grams(100,.9),90)
        with self.assertRaises(ValueError):volume_grams(100,0)
    def test_recipe_missing_propagates(self):
        r=recipe([({'energy_kcal_100g':100},100),({'energy_kcal_100g':200},50)],200)
        self.assertEqual(r['total']['energy_kcal'],200)
        self.assertEqual(r['per_100g']['energy_kcal'],100)
        self.assertIsNone(r['total']['protein_g'])
        with self.assertRaises(ValueError):recipe([],100)

if __name__=='__main__':unittest.main()
