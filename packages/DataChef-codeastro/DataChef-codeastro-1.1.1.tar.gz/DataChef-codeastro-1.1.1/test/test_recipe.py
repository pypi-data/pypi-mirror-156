from cgi import test
import pytest
import numpy as np

from DataChef import ingredient_functions as ing_funcs
from DataChef import mix_functions as mix_funcs
from DataChef import recipe
from DataChef.recipe import Recipe
from DataChef.ingredient import Ingredient

def test_plus_mix_func():
    pass
def test_minus_mix_func():
    pass
def test_multiply_mix_func():
    pass
def test_divide_mix_func():
    pass
def test_convolve_mix_func():
    pass

def test_not_ing_obj_in_add_ingredeient():
    """
    Check that the if the ingredient parameter given is not 
    an Ingredient object, the function would raise warning.
    """
    test_ing = np.array([1,2,3])
    test_rec = Recipe()
    
    assert test_rec.add_ingredient(test_ing, mix_funcs.add) is None
# test_not_ing_obj_in_add_ingredeient()

def test_idx_in_add_ingredeient():
    """
    Check that the if the index parameter is given,
    the ingredient is correctly insert at the index.
    """
    ing_line  = Ingredient(ing_funcs.line, "line",m=10, b=1)
    ing_line2  = Ingredient(ing_funcs.line, "line2",m=5, b=1)
    ing_line3  = Ingredient(ing_funcs.line, "line3",m=5, b=1)

    idx1 = 0; idx2 = 5
    test_rec = Recipe()
    test_rec.add_ingredient(ing_line,mix_funcs.add)
    test_rec.add_ingredient(ing_line,mix_funcs.add)
    test_rec.add_ingredient(ing_line2,mix_funcs.add,idx1)
    test_rec.add_ingredient(ing_line3,mix_funcs.add,idx2)

    assert 'line2' == test_rec.ingredients[idx1].label
    assert 'line3' == test_rec.ingredients[len(test_rec.ingredients)-1].label
test_idx_in_add_ingredeient()

def test_add_recipe():
    """
    Check that the if the variable given is not Ingredient object, the function would raise warning.
    """
    ing_line  = Ingredient(ing_funcs.line, "line",m=10, b=1)
    ing_line2  = Ingredient(ing_funcs.line, "line2",m=5, b=1)
    minirecipe1 = Recipe()
    minirecipe1.add_ingredient(ing_line, mix_funcs.add)
    minirecipe1.add_ingredient(ing_line2, mix_funcs.add)

    ing_par = Ingredient(ing_funcs.parabola, "parabola", a=1, b=2, c=1)
    ing_uni = Ingredient(ing_funcs.uniform, "white noise", scale=1.5)
    minirecipe2 = Recipe()
    minirecipe2.add_ingredient(ing_par, mix_funcs.add)
    minirecipe2.add_ingredient(ing_uni, mix_funcs.add)

    minirecipe1.add_recipe(minirecipe2)
    assert 'parabola' == minirecipe1.ingredients[2].label
    assert 'white noise' == minirecipe1.ingredients[3].label

# test_add_recipe()

