import numpy as np
import matplotlib.pyplot as plt
from DataChef.ingredient import Ingredient
from uncertainties import unumpy

class Recipe():
    """A list of steps to cook up a simulated data set.

    A Recipe stores a list of Ingredients and the method by which they will be mixed
    in to generate a simulated data set. 
    
    Args:
        label (:obj:`str`, optional) : the name of the Recipe

    Attributes:
        ingredients (:obj:`list` of :obj:`Ingredient`): list of Ingredients in the Recipe, in order of application
        mix_funcs (:obj:`list`): list the mixing functions by which Ingredients will be added, in order of application
        label (:obj:`str`): the name of the Recipe
    """
    
    def __init__(self, label="recipe"):
        """Initialize a Recipe object.

        Recipes store a list of Ingredients and the methods that they will be mixed
        into the dataset. Use 

        Args:
            label (:obj:`str`, optional): the name of the Recipe
        """ 

        self.ingredients = []
        self.mix_funcs = []
        self.label = label

    def add_ingredient(self, ingredient, mix_func, idx=None):
        """Add an Ingredient object to a Recipe.

        Args:
            ingredient (:obj:`Ingredient object`): The Ingredient object to be added
            mix_func(:func:`function`): A function that takes in two arrays of equal length, mixes them in some way into a 1D array and returns it
            idx (:obj:`int`, optional): insert an ingredient at the given index. Only works when the recipe list reaches this index.
        """

        if type(ingredient) is not Ingredient:
            print("Warning Message: ingredient must be Ingredient object.")
            return None

        if idx is None:
            self.ingredients.append(ingredient)
            self.mix_funcs.append(mix_func)
        else :
            if idx > len(self.ingredients):
                print("Warning Message: given index not exist, add ingredient to the last index.")
            self.ingredients.insert(idx, ingredient)
            self.mix_funcs.insert(idx, mix_func)

    def add_recipe(self, recipe):
        """Adds one Recipe line by line into this one. 
        
        Currently ignores orders of operation, but this funcitonality will be added soon.

        Args:
            recipe (:obj:`Recipe`): The Recipe object to be added
        """
        # TO DO: Update to respect order of operations (talk to Rae)
        for ing, mix in zip(recipe.ingredients, recipe.mix_funcs):
            self.ingredients.append(ing)
            self.mix_funcs.append(mix)          

    def print(self):
        """Print a summary of the Recipe, including its Ingredients and mixing functions."""
        
        print('Recipe Summary')
        for idx, (ing, mix) in enumerate(zip(self.ingredients, self.mix_funcs)):
            print(str(idx) + ': ' + ing.label + ', ' + mix.__name__)  

    def plot(self, grid, marker='.', export_eval=None, export_cum=None, seed=None):
        """Plots the output of a recipe.

        Args:
            grid (:obj:`1D array`): The x grid that the recipe will be evaluated on
            seed (:obj:`int`, optional): A seed for random number generation via the numpy package.
        """

        output = Recipe.cook_recipe(self, grid, export_eval, export_cum, seed)
        final = output[0]
        plt.plot(grid, final, marker=marker, c='k')
        ing_labels = ""
        for ing in self.ingredients:
            ing_labels += ing.label + ", "
        ing_labels = ing_labels[0:-2]
        plt.title(f"Ingredients: {ing_labels}")

    def cook_recipe(self, grid, seed=None, export_eval=None, export_cum=None):
        """Evaluates the recipe on a grid of x-values.

        Args:
            grid (:obj:`1D array`): The x grid that the recipe will be evaluated on
            seed (:obj:`int`, optional): A seed for random number generation via the numpy package.
            export_eval (:obj:`bool`, optional): If True, exports `ings_evaluated` to a .csv file 
            export_cum (:obj:`bool`, optional): If True, exports `cumulative` to a .csv file

        Returns:
            y (:obj:`1D array`): The y values calculated by the recipe
            ings_evaluated (:obj:`2D array`): Stores the output of ingredient.eval() for each 
                ingredient in the recipe. The `i`th row corresponds to ingredient at the `i`th 
                step of the recipe.
            cumulative (:obj:`2D array`): Stores the y-values at each step of the recipe. The 
                `i`th row corresponds the `i`th step of the recipe.
            errs_evaluated (:obj:`2D array`): Stores the errorbars from ingredient.eval() for each 
                ingredient in the recipe. The `i`th row corresponds to ingredient at the `i`th 
                step of the recipe.
            errs_cumulative (:obj:`2D array`): Stores the errorbars at each step of the recipe. The 
                `i`th row corresponds the `i`th step of the recipe.
        """
        # TO DO: Make compatible with grids of higher dimention
        if seed is not None:
            np.random.seed(seed)

        # array to store the y and yerr array for each ingredient evaluated over the grid
        ings_evaluated = np.zeros((len(self.ingredients),len(grid)))
        errs_evaluated = np.zeros((len(self.ingredients),len(grid)))

        # array to store the state of the "base" after each ingredient is added
        cumulative = np.zeros((len(self.ingredients),len(grid)))
        errs_cumulative = np.zeros((len(self.ingredients),len(grid)))

        # add in the first ingredient
        y = self.ingredients[0].eval(grid)
        ings_evaluated[0] = unumpy.nominal_values(y)
        errs_evaluated[0] = unumpy.std_devs(y)
        cumulative[0] = unumpy.nominal_values(y)
        errs_cumulative[0] = unumpy.std_devs(y)
        
        # loop through the ingredients and add them in
        for idx, (ing, mix) in enumerate(zip(self.ingredients[1:], self.mix_funcs[1:])) :
            # evaluate the ingredient on the grid
            y = ing.eval(grid)
            ings_evaluated[idx+1,:] = unumpy.nominal_values(y)
            errs_evaluated[idx+1,:] = unumpy.std_devs(y)

            # mix the ingredient into the dish
            cumulative[idx+1] = unumpy.nominal_values(mix(cumulative[idx],y))
            errs_cumulative[idx+1] = unumpy.std_devs(mix(cumulative[idx],y))

        # export the evaluated ingredient to csv
        if export_eval is not None:
            np.savetxt(fname=export_eval, X=y)
        if export_cum is not None:
            np.savetxt(fname=export_cum, X=cumulative)
            
        return cumulative[-1], ings_evaluated, cumulative, errs_evaluated, errs_cumulative