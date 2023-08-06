import matplotlib.pyplot as plt

class Ingredient():
    def __init__(self, func, label, **kwargs):
        self.func = func
        self.kwargs = kwargs
        self.label = label

    def plot(self, x):
        plt.plot(x, self.eval(x), marker='.', c='k')
        plt.title(f"Ingredient '{self.label}'")
    
    def eval(self, x):
        """Evaluates the functional form of the ingredient on an array of x values."""
        return self.func(x, **self.kwargs)