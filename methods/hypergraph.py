"""Centered-product projection for susceptible-infected hypergraph coupling."""
from collections import defaultdict
from itertools import combinations
from math import factorial
import numpy as np


def centered_coefficients(edges, receiver, mean=0.5):
    """Coefficients of source products about a common mean.

    F_i=(1-x_i) sum_{e contains i} (|e|-1)! product_{j in e excluding i} x_j.
    Combine overlapping contributions before squaring. Node IDs are arbitrary
    hashable integers, provided receiver and edges use the same indexing.
    """
    coefficients = defaultdict(float)
    for edge in edges:
        if len(set(edge)) != len(edge): raise ValueError('repeated node in edge')
        if receiver not in edge: continue
        source = sorted(set(edge)-{receiver}); degree = len(source)
        for n in range(degree+1):
            for subset in combinations(source,n):
                coefficients[subset] += factorial(degree)*mean**(degree-n)
    return dict(coefficients)


def product_law_risk(coefficients, q, mean=0.5, variance=1/12):
    """Exact risk for independent coordinates sharing mean and variance.

    Order q retains receiver dependence and source subsets of size <=q-1.
    The receiver factor contributes E(1-X_i)^2=(1-mean)^2+variance.
    """
    if q < 1 or int(q) != q or variance < 0: raise ValueError('invalid q or variance')
    return ((1-mean)**2+variance)*sum(c*c*variance**len(S)
              for S,c in coefficients.items() if len(S)>=q)


def beta_variance(alpha):
    if alpha <= 0: raise ValueError('alpha must be positive')
    return 1/(4*(2*alpha+1))


def evaluate_projection(coefficients, x, receiver, q):
    """Evaluate at zero-based indexed state arrays, with mean 1/2."""
    x = np.asarray(x)
    value = np.zeros(x.shape[:-1])
    for S,c in coefficients.items():
        if len(S)<=q-1:
            value += c*(np.prod(x[...,list(S)]-0.5,axis=-1) if S else 1)
    return (1-x[...,receiver])*value
