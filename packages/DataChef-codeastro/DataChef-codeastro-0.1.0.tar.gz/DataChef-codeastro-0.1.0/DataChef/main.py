#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from recipe import Recipe
from ingredient import Ingredient
import ingredient_functions as ing_funcs
import mix_functions as mix_funcs

if __name__ == "__main__":
    # make some ingredients for testing
    ing  = Ingredient(ing_funcs.line, "line", is_signal=True, m=10, b=1)
    ing2 = Ingredient(ing_funcs.line, "line", is_signal=True, m=-5, b=1)
    ing3 = Ingredient(ing_funcs.white_noise, "white noise", is_signal=False, scale=1.5, shift=2)

    # mini recipe
    m1 = Ingredient(ing_funcs.parabola, "parabola", True, a=1, b=2, c=1)
    m2 = Ingredient(ing_funcs.white_noise, "white noise", is_signal=False, scale=1.5)
    minirecipe = Recipe()
    minirecipe.add_ingredient(m1, mix_funcs.add)
    minirecipe.add_ingredient(m2, mix_funcs.add)

    # Run test function on an ingredient
    # ing.test(np.linspace(0,10,11))

    ing_line  = Ingredient(ing_funcs.line, "line",m=10, b=1)
    ing_parab = Ingredient(ing_funcs.parabola, "parabola", a=-2, b=0, c=3)
    ing_cubic = Ingredient(ing_funcs.cubic, "cubic", a=2, b=0, c=0, d=-5)
    ing_sine = Ingredient(ing_funcs.sinusoid, "sinusoid", phase=0, amplitude=4, period=np.pi)
    
    ing_unif = Ingredient(ing_funcs.uniform, "white noise", shift=0, scale=5)
    ing_gaus = Ingredient(ing_funcs.gaussian, "gaussian", mean=5, stdev=2)
    ing_pois = Ingredient(ing_funcs.poisson, "poisson", lam=2)

    # ingredients that use a custom function
    # def custom(x, a, b, c):
    #     print(a,b,c)
    #     return a*x + b + c
    # ing_cust = Ingredient(custom, "custom", a=1, b=2, c=3)
    
    # add ingredients to the Recipe
    recipe = Recipe()
    recipe.add_ingredient(ing , mix_funcs.add)
    recipe.add_ingredient(ing2, mix_funcs.add)
    recipe.add_ingredient(ing3, mix_funcs.add)
    recipe.add_recipe(minirecipe)

    rec = Recipe()
    rec.add_ingredient(ing_sine, mix_funcs.add)
    rec.add_ingredient(ing_parab, mix_funcs.add)
    rec.add_ingredient(ing_unif, mix_funcs.add)

    # Cook the recipe
    x = np.linspace(-10,10,101)
    y, ing_eval, ing_comp = rec.cook_recipe(x, export_eval='output/eval_test.csv', 
                                               export_cum='output/cum_test.csv')

    # test print_recipe()
    rec.print()
    rec.plot(x)
    plt.show()


    # plot each indiviual ingredient
    for i in range(len(recipe.ingredients)):
        plt.plot(x, ing_eval[i])
        plt.show()
        

