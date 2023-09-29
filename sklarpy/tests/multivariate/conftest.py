# Contains pytest fixtures for testing SklarPy multivariate code
import pandas as pd
import numpy as np
import pytest
import scipy.stats

from sklarpy.multivariate import distributions_map

num: int = 100
d: int = 2


@pytest.fixture(scope="session", autouse=True)
def mvt_continuous_data():
    return scipy.stats.multivariate_normal.rvs(size=(num, d))


@pytest.fixture(scope="session", autouse=True)
def mvt_discrete_data():
    poisson_data: np.ndarray = scipy.stats.poisson.rvs(4, size=(num, d + 1))
    for i in range(1, d):
        poisson_data[:, i] = poisson_data[:, i] + poisson_data[:, i + 1]
    return poisson_data[:, :-1]


@pytest.fixture(scope="session", autouse=True)
def pd_mvt_continuous_data():
    data: np.ndarray = scipy.stats.multivariate_normal.rvs(size=(num, d))
    return pd.DataFrame(data, columns=[f'var {i}' for i in range(d)])


@pytest.fixture(scope="session", autouse=True)
def pd_mvt_discrete_data():
    poisson_data: np.ndarray = scipy.stats.poisson.rvs(4, size=(num, d + 1))
    for i in range(1, d):
        poisson_data[:, i] = poisson_data[:, i] + poisson_data[:, i + 1]
    return pd.DataFrame(poisson_data[:, :-1], columns=[f'var {i}' for i in
                                                       range(d)])


@pytest.fixture(scope="session", autouse=True)
def mv_dists_to_test():
    return distributions_map['all']


@pytest.fixture(scope="session", autouse=True)
def params_2d():
    return {
        'multivariate_normal': (
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.22604687e+00, 9.60076079e-18],
                      [9.60076079e-18, 7.30245004e-01]])),

        'multivariate_student_t': (
            100.0,
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.20152593, 0.19624622],
                      [0.19624622, 0.7156401]])),

        'multivariate_gen_hyperbolic': (
            -1.1788364839820724, 10.0, 10.0,
            np.array([[0.84415713], [-0.45785498]]),
            np.array([[1.2253664, 0.26909617],
                      [0.26909617, 0.75701993]]),
            np.array([[-1.00453046], [0.56047505]])),

        'multivariate_marginal_hyperbolic': (
            6.430016040119274, 10.0,
            np.array([[0.69052415], [-0.39804144]]),
            np.array([[1.22869356, 0.2616279],
                      [0.2616279, 0.75174415]]),
            np.array([[-0.82414258], [0.48692467]])),

        'multivariate_hyperbolic': (
            5.584106488470228, 10.0,
            np.array([[0.65995643], [-0.3874908]]),
            np.array([[1.2296575, 0.26089854],
                      [0.26089854, 0.75084492]]),
            np.array([[-0.78967095], [0.47438798]])),

        'multivariate_nig': (
            8.986208938433768, 10.0,
            np.array([[0.78169119], [-0.43129769]]),
            np.array([[1.22628047, 0.26411374],
                      [0.26411374, 0.7542892]]),
            np.array([[-0.92734838], [0.52616235]])),

        'multivariate_skewed_t': (
            10.0,
            np.array([[0.15711164], [-0.10459758]]),
            np.array([[1.22892318, 0.21921408],
                      [0.21921408, 0.7350084]]),
            np.array([[-0.20360485], [0.13766299]])),

        'multivariate_sym_gen_hyperbolic': (
            -0.4268651272656109, 10.0, 10.0,
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.22604687, 0.20025125],
                      [0.20025125, 0.730245]])),

        'multivariate_sym_marginal_hyperbolic': (
            7.523270258556909, 10.0,
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.22604687, 0.20025125],
                      [0.20025125, 0.730245]])),

        'multivariate_sym_hyperbolic': (
            6.610028122530992, 10.0,
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.22604687, 0.20025125],
                      [0.20025125, 0.730245]])),

        'multivariate_sym_nig': (
            10.0, 10.0,
            np.array([[-0.09739442], [0.06748115]]),
            np.array([[1.22604687, 0.20025125],
                      [0.20025125, 0.730245]]))
    }


@pytest.fixture(scope="session", autouse=True)
def params_3d():
    return {
        'multivariate_normal': (
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.21898949e+00, 9.34403992e-17, 8.06538495e-17],
                      [3.91669234e-18, 9.03438954e-01, 7.39590407e-19],
                      [5.18678009e-18, 3.39803556e-17, 1.05766110e+00]])),

        'multivariate_student_t': (
            100.0,
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.1946097, 0.09775865, -0.00776843],
                      [0.09775865, 0.88537018, 0.08621716],
                      [-0.00776843,  0.08621716, 1.03650788]])),

        'multivariate_gen_hyperbolic': (
            -1.782382671254414, 10.0, 10.0,
            np.array([[-0.62581127], [-1.87660553], [0.13564066]]),
            np.array([[ 1.38090727e+00, -2.01241655e-04, -2.60836067e-03],
                      [-2.01241655e-04,  6.86684932e-01,  1.23061470e-01],
                      [-2.60836067e-03, 1.23061470e-01, 1.22915669e+00]]),
            np.array([[0.63853468], [2.00090016], [-0.11382825]])),

        'multivariate_marginal_hyperbolic': (
            6.205679755772674, 10.0,
            np.array([[-0.4760037], [-1.50649459], [0.0978438 ]]),
            np.array([[1.33664701, 0.03084231, -0.0052302],
                      [0.03084231, 0.73684715, 0.1103901],
                      [-0.0052302, 0.1103901, 1.17990614]]),
            np.array([[0.44089418], [1.4870162], [-0.06682156]])),

        'multivariate_hyperbolic': (
            4.669931146010268, 10.0,
            np.array([[-0.43035465], [-1.40305972], [0.08801923]]),
            np.array([[1.32964083, 0.03793152, -0.00580953],
                      [0.03793152, 0.74609703, 0.10788308],
                      [-0.00580953, 0.10788308, 1.17118297]]),
            np.array([[0.38622221], [1.35541132], [-0.05549939]])),

        'multivariate_nig': (
            8.517549891625043, 10.0,
            np.array([[-0.54136409], [-1.66194387], [0.11216012]]),
            np.array([[1.34739657, 0.02110339, -0.00440445],
                      [0.02110339, 0.72340899, 0.11398558],
                      [-0.00440445, 0.11398558, 1.19285811]]),
            np.array([[0.52083656], [1.68621739], [-0.08371633]])),

        'multivariate_skewed_t': (
            10.0,
            np.array([[-0.1552794], [-0.58786565], [0.03910667]]),
            np.array([[ 1.25348961, 0.0871567, -0.00803451],
                      [0.0871567, 0.8514119, 0.09138582],
                      [-0.00803451, 0.09138582, 1.09025713]]),
            np.array([[0.07567869], [0.38571318], [-0.00336706]])),

        'multivariate_sym_gen_hyperbolic': (
            -0.33835936636262204, 10.0, 10.0,
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.21898949, 0.09975372, -0.00792697],
                      [0.09975372, 0.90343895, 0.08797669],
                      [-0.00792697, 0.08797669, 1.0576611]])),

        'multivariate_sym_marginal_hyperbolic': (
            7.799728823974279, 10.0,
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.21898949, 0.09975372, -0.00792697],
                      [0.09975372, 0.90343895, 0.08797669],
                      [-0.00792697, 0.08797669, 1.0576611]])),

        'multivariate_sym_hyperbolic': (
            5.992259894031568, 10.0,
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.21898949, 0.09975372, -0.00792697],
                      [0.09975372, 0.90343895, 0.08797669],
                      [-0.00792697, 0.08797669, 1.0576611]])),

        'multivariate_sym_nig': (
            10.0, 9.96376429525435,
            np.array([[-0.06068104], [-0.10572418], [0.03489784]]),
            np.array([[1.21898949, 0.09975372, -0.00792697],
                      [0.09975372, 0.90343895, 0.08797669],
                      [-0.00792697, 0.08797669, 1.0576611]]))
    }
