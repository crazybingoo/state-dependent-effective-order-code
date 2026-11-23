"""Finite-dictionary approximation and bounded-loss uncertainty primitives."""
import numpy as np


def weighted_projection(features, target, weights=None, ridge=0.0):
    """Fit a frozen target; intercept is unpenalized, features use weighted scale.

    Returns intercept, raw-feature coefficients and in-sample candidate loss.
    A finite dictionary provides an upper bound on complete-space risk.
    """
    X=np.asarray(features,dtype=float); y=np.asarray(target,dtype=float)
    if X.ndim!=2 or y.shape!=(len(X),) or len(X)<2 or ridge<0: raise ValueError('invalid inputs')
    w=np.ones(len(y)) if weights is None else np.asarray(weights,dtype=float)
    if w.shape!=y.shape or np.any(w<0) or w.sum()<=0: raise ValueError('invalid weights')
    w=w/w.sum(); mu=w@X; ym=w@y
    scale=np.maximum(np.sqrt(w@((X-mu)**2)),1e-12)
    Z=(X-mu)/scale; A=Z*np.sqrt(w[:,None]); b=(y-ym)*np.sqrt(w)
    # A stacked least-squares solve also supports rank-deficient dictionaries.
    coef=np.linalg.lstsq(np.vstack((A,np.sqrt(ridge)*np.eye(X.shape[1]))),
                        np.r_[b,np.zeros(X.shape[1])],rcond=1e-10)[0]/scale
    intercept=ym-mu@coef
    return float(intercept),coef,float(w@((y-intercept-X@coef)**2))


def empirical_bernstein(losses, loss_bound, delta):
    """Two-sided clipped interval using the manuscript's bounded-loss radius.

    Each entry must be one independent sampling unit (e.g. an antithetic-pair
    average). The supplied loss_bound must be a valid a priori uniform bound.
    """
    x=np.asarray(losses,dtype=float); n=x.size
    if x.ndim!=1 or n<2 or loss_bound<=0 or not 0<delta<1: raise ValueError('invalid inputs')
    if np.any(x<0) or np.any(x>loss_bound): raise ValueError('loss outside supplied bound')
    radius=np.sqrt(2*x.var(ddof=1)*np.log(2/delta)/n)+7*loss_bound*np.log(2/delta)/(3*(n-1))
    return max(0.0,float(x.mean()-radius)),min(loss_bound,float(x.mean()+radius))
