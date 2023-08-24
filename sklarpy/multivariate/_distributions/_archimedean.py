# contains code for archimedean copulas
import numpy as np
from abc import abstractmethod
from typing import Union, Tuple
import scipy.stats
import scipy.optimize

from sklarpy.multivariate._prefit_dists import PreFitContinuousMultivariate
from sklarpy._utils import get_iterator, FitError
from sklarpy.misc import debye

__all__ = ['multivariate_clayton_gen', 'multivariate_gumbel_gen', 'bivariate_frank_gen']


class multivariate_archimedean_base_gen(PreFitContinuousMultivariate):
    _DATA_FIT_METHODS = ("mle", 'inverse_kendall_tau', 'low_dim_mle')
    _DEFAULT_STRICT_BOUNDS: tuple
    _DEFAULT_BOUNDS: tuple
    _N_PARAMS: int

    @abstractmethod
    def _param_range(self, d: int) -> Tuple[Tuple[float, float], list]:
        pass

    def _check_params(self, params: tuple, **kwargs) -> None:
        # checking correct number of params passed
        super()._check_params(params)

        # checking valid theta and dimensions parameters
        d = self._get_dim(params)
        if not isinstance(d, int):
            raise TypeError("d (dimensions parameter) must be an integer.")
        elif d < 2:
            raise ValueError("d (dimensions parameter) must be greater than or equal to 2.")

        theta = params[0]
        bounds, excluded = self._param_range(d=d)
        if not (isinstance(theta, float) or isinstance(theta, int)):
            raise TypeError("theta must be a scalar value.")
        elif (not bounds[0] <= theta <= bounds[1]) or theta in excluded:
            excluded_msg: str = " " if len(excluded) == 0 else f" cannot be any of {excluded} and "
            raise ValueError(f"theta parameter{excluded_msg}must lie within {bounds[0]} <= theta <= {bounds[1]} when d={d}. However, theta={theta}")

    @abstractmethod
    def _generator(self, u: np.ndarray, params: tuple) -> np.ndarray:
        pass

    @abstractmethod
    def _generator_inverse(self, t: np.ndarray, params: tuple) -> np.ndarray:
        pass

    def _cdf(self, x: np.ndarray, params: tuple, **kwargs) -> np.ndarray:
        shape: tuple = x.shape

        show_progress: bool = kwargs.get('show_progress', True)
        iterator = get_iterator(range(shape[1]), show_progress, "calculating cdf values")

        t: np.ndarray = np.zeros((shape[0], ), dtype=float)
        for i in iterator:
            t += self._generator(u=x[:, i], params=params)
        return self._generator_inverse(t=t, params=params)

    def _G_hat(self, t: np.ndarray, params: tuple) -> np.ndarray:
        return self._generator_inverse(t=t, params=params)

    @abstractmethod
    def _v_rvs(self, size: int, params: tuple) -> np.ndarray:
        pass

    def _get_dim(self, params: tuple) -> int:
        return 2

    def _rvs(self, size: int, params: tuple) -> np.ndarray:
        v: np.ndarray = self._v_rvs(size=size, params=params)
        d: int = self._get_dim(params=params)
        x: np.ndarray = np.random.uniform(size=(size, d))
        t: np.ndarray = -np.log(x) / v
        return self._G_hat(t=t, params=params)

    def _get_bounds(self, data: np.ndarray, as_tuple: bool, **kwargs) -> Union[dict, tuple]:
        d: int = data.shape[1]
        theta_bounds: tuple = self._DEFAULT_STRICT_BOUNDS if d > 2 else self._DEFAULT_BOUNDS
        default_bounds: dict = {'theta': theta_bounds}
        return super()._get_bounds(default_bounds, d, as_tuple, **kwargs)

    def _get_low_dim_theta0(self, data: np.ndarray, bounds: tuple, copula: bool) -> np.ndarray:
        theta0: float = np.random.uniform(*bounds[0])
        return np.array([theta0], dtype=float)

    def _low_dim_theta_to_params(self, theta: np.ndarray, d: int) -> tuple:
        return theta[0], d

    def _get_low_dim_mle_objective_func_args(self, data: np.ndarray, **kwargs) -> tuple:
        return data.shape[1],

    def _inverse_kendall_tau_calc(self, kendall_tau: float) -> float:
        pass

    def _inverse_kendall_tau(self, data: np.ndarray, **kwargs) -> float:
        d: int = data.shape[1]
        if d != 2:
            raise FitError("Archimedean copulas can only be fit using inverse kendall's tau when the number of variables is exactly 2.")

        kendall_tau: float = scipy.stats.kendalltau(data[:, 0], data[:, 1]).statistic
        theta: float = self._inverse_kendall_tau_calc(kendall_tau=kendall_tau)
        params: tuple = (theta, d)
        try:
            self._check_params(params=params)
        except Exception:
            raise FitError(f"cannot fit {self.name} using inverse kendall's tau method. This is because the fitted theta parameter likely lies outside its permitted range.")
        return (theta, d), ~np.isinf(theta)

    def _mle(self, data: np.ndarray, **kwargs) -> tuple:
        return super()._low_dim_mle(data, **kwargs)

    def _fit_given_data_kwargs(self, method: str, data: np.ndarray, **user_kwargs) -> dict:
        if method in ('mle', 'low_dim_mle'):
            return super()._fit_given_data_kwargs('low_dim_mle', data, **user_kwargs)
        return {'copula': True}

    def _fit_given_params_tuple(self, params: tuple, **kwargs) -> Tuple[dict, int]:
        d: int = self._get_dim(params=params)
        return {'theta': params[0], 'd': d}, d

    def num_scalar_params(self, d: int, copula: bool, **kwargs) -> int:
        return self._N_PARAMS


class multivariate_clayton_gen(multivariate_archimedean_base_gen):
    _DEFAULT_STRICT_BOUNDS = (0, 100.0)
    _DEFAULT_BOUNDS = (-1, 100.0)
    _N_PARAMS = 2

    def _param_range(self, d: int) -> Tuple[Tuple[float, float], list]:
        lb: float = 0.0 if d > 2 else -1
        return (lb, np.inf), [0.0]

    def _generator(self, u: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return (np.power(u, -theta) - 1) / theta

    def _generator_inverse(self, t: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return np.power((theta * t) + 1, -1 / theta)

    def _G_hat(self, t: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return np.power(t + 1, -1 / theta)

    def _v_rvs(self, size: int, params: tuple) -> np.ndarray:
        theta = params[0]
        if theta < 0:
            raise NotImplementedError("cannot generate random variables for Clayton Copula when theta parameter is not positive.")
        return scipy.stats.gamma.rvs(a=1/theta, scale=1, size=(size, 1))

    def _get_dim(self, params: tuple) -> int:
        return params[1]

    def _inverse_kendall_tau_calc(self, kendall_tau: float) -> float:
        return 2 * kendall_tau / (1 - kendall_tau)

    def _logpdf(self, x: np.ndarray, params: tuple,  **kwargs) -> np.ndarray:
        theta, d = params

        # common calculations
        theta_inv: float = 1/theta

        # calculating evaluating generator function
        gen_sum: np.ndarray = np.zeros((x.shape[0], ), dtype=float)
        log_cs: float = 0.0
        log_gs: float = 0.0
        for i in range(d):
            gen_val: np.ndarray = self._generator(u=x[:, i], params=params)
            gen_sum += gen_val

            log_cs += np.log(theta_inv + d - i)
            log_gs += np.log((theta*gen_val) + 1)

        return (d * np.log(theta)) - ((theta_inv + d) * np.log((theta * gen_sum) + 1)) + log_cs + ((theta_inv + 1) * log_gs)


class multivariate_gumbel_gen(multivariate_archimedean_base_gen):
    _DEFAULT_STRICT_BOUNDS = (1.0, 100.0)
    _DEFAULT_BOUNDS = _DEFAULT_STRICT_BOUNDS
    _N_PARAMS = 2

    def _param_range(self, d: int) -> Tuple[Tuple[float, float], list]:
        return (1.0, np.inf), []

    def _generator(self, u: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return np.power(-np.log(u), theta)

    def _generator_inverse(self, t: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return np.exp(-np.power(t, 1/theta))

    def _v_rvs(self, size: int, params: tuple) -> np.ndarray:
        theta: float = params[0]
        c: float = np.power(np.cos(np.pi/(2*theta)), theta)
        return scipy.stats.levy_stable.rvs(1/theta, 1.0, c, 0.0, size=(size, 1))

    def _get_dim(self, params: tuple) -> int:
        return params[1]

    def _inverse_kendall_tau_calc(self, kendall_tau: float) -> float:
        return 1 / (1 - kendall_tau)

    def _DK_psi(self, t: np.ndarray, params: tuple, K: int) -> np.ndarray:
        if K == 0:
            return self._generator_inverse(t=t, params=params)
        theta: float = params[0]
        theta_inv: float = 1/theta

        DK_psi: np.ndarray = np.zeros(t.shape, dtype=float)
        for j in range(K):
            prod = np.array([theta_inv - i + 1 for i in range(1, K - j + 1)]).prod()
            DK_psi -= self._DK_psi(t=t, params=params, K=j) * np.power(t, theta_inv - K + j) * prod
        return DK_psi

    def _logpdf(self, x: np.ndarray, params: tuple,  **kwargs) -> np.ndarray:
        theta, d = params

        # calculating evaluating generator function
        gen_sum: np.ndarray = np.zeros((x.shape[0],), dtype=float)
        log_gs: float = 0.0
        for i in range(d):
            gen_val: np.ndarray = self._generator(u=x[:, i], params=params)
            gen_sum += gen_val

            log_gs -= (((1/theta) - 1) * np.log(gen_val)) + np.log(x[:, i])

        # calculating d-th derivative of generator inverse
        Dd_psi: np.ndarray = self._DK_psi(t=gen_sum, params=params, K=d)
        return np.log(np.abs(Dd_psi)) + (d*np.log(theta)) + log_gs


class bivariate_frank_gen(multivariate_archimedean_base_gen):
    _DEFAULT_STRICT_BOUNDS = (-100.0, 100.0)
    _DEFAULT_BOUNDS = _DEFAULT_STRICT_BOUNDS
    _N_PARAMS = 1

    def _param_range(self, d: int) -> Tuple[Tuple[float, float], list]:
        return (-np.inf, np.inf), [0.0]

    def _generator(self, u: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return -np.log((np.exp(-theta*u) - 1) / (np.exp(-theta) - 1))

    def _generator_inverse(self, t: np.ndarray, params: tuple) -> np.ndarray:
        theta: float = params[0]
        return -(theta**-1) * np.log(1 + np.exp(-t) * (np.exp(-theta) - 1))

    def _rvs(self, size: int, params: tuple) -> np.ndarray:
        theta: float = params[0]
        rvs: np.ndarray = np.random.uniform(size=(size, 2))
        rvs[:, 1] = - (theta**-1) * np.log(1 + (((1 - np.exp(theta**-1)) * rvs[:, 1]) / ((rvs[:, 1] * (np.exp(-theta*rvs[:, 0]) - 1)) - np.exp(-theta*rvs[:, 0]))))
        return rvs

    def __root_to_solve(self, theta: float, kendall_tau: float) -> float:
        return 1 - (4 * (theta ** -1) * (1 - debye(1, theta))) - kendall_tau

    def _inverse_kendall_tau_calc(self, kendall_tau: float) -> float:
        factor = 2.
        left, right = -factor, factor

        while self.__root_to_solve(left, kendall_tau) > 0.:
            left, right = left * factor, left
        # left is now such that func(left) <= tau
        # if right has changed, then func(right) > tau

        while self.__root_to_solve(right, kendall_tau) < 0.:
            left, right = right, right * factor
        # right is now such that func(right) >= tau

        return scipy.optimize.brentq(self.__root_to_solve, left, right, args=(kendall_tau,))

    def _logpdf(self, x: np.ndarray, params: tuple, **kwargs) -> np.ndarray:
        theta: float = params[0]
        if theta <= 0:
            # logpdf is undefined for theta <= 0
            self._not_implemented('logpdf')

        log_numerator: np.ndarray = np.log(theta) + np.log(np.exp(theta) - 1) + (theta * (x.sum(axis=1) + 1))
        log_denominator: np.ndarray = 2 * np.log(np.exp(theta * x.sum(axis=1)) - np.exp(theta * (x[:, 0] + 1)) - np.exp(theta * (x[:, 1] + 1)) + np.exp(theta))
        return log_numerator - log_denominator

    def _pdf(self, x: np.ndarray, params: tuple, **kwargs) -> np.ndarray:
        theta: float = params[0]

        numerator: np.ndarray = theta * (np.exp(theta) - 1) * np.exp(theta * (x.sum(axis=1) + 1))
        denominator: np.ndarray = np.power(np.exp(theta * x.sum(axis=1)) - np.exp(theta * (x[:, 0] + 1)) - np.exp(theta * (x[:, 1] + 1)) + np.exp(theta), 2)
        return numerator / denominator