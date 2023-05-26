# contains code for fitting a discrete uniform distribution to data
import numpy as np

__all__ = ['duniform_fit']


def duniform_fit(data: np.ndarray) -> tuple:
    """Fitting function for the discrete uniform distribution. Returns the minimum and maximum values of the sample.

    Math
    =====
    a = min(x)
    b = max(x)

    See Also:
    ==========
    https://en.wikipedia.org/wiki/Discrete_uniform_distribution

    Parameters
    ----------
    data: np.ndarray
        The data to fit to the discrete uniform distribution in a flattened numpy array.

    Returns
    -------
    estimator: tuple
       (a, b)
    """
    return data.min(), data.max() + 1
