# Contains useful scalar values

__all__ = ['prob_bounds', 'near_zero']

near_zero: float = 10**-3
prob_bounds: tuple = (near_zero, 1-near_zero)
