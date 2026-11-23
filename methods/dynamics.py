"""Residual propagation, response matching and regional error bounds."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm, eigvalsh


def linear_error(A, residual, time):
    """e'=A e-r, e(0)=0, r=full-minus-reduced; singular A is permitted."""
    A=np.asarray(A,dtype=float); r=np.asarray(residual,dtype=float)
    n=len(r); aug=np.zeros((n+1,n+1));aug[:n,:n]=A;aug[:n,n]=-r
    return expm(aug*time)[:n,n]


def variational_error(jacobian, residual, times, dimension, hessian=None):
    """Propagate along a supplied full trajectory.

    Inputs are time-indexed functions evaluated along that trajectory. The
    optional Hessian of the reduced field includes the quadratic Taylor term.
    This is an approximation, not an autonomous rollout or a certificate.
    """
    times=np.asarray(times,dtype=float)
    if len(times)<2 or np.any(np.diff(times)<=0): raise ValueError('times must increase')
    def rhs(t,e):
        value=np.asarray(jacobian(t))@e-np.asarray(residual(t))
        if hessian is not None: value+=0.5*np.einsum('ijk,j,k->i',hessian(t),e,e)
        return value
    sol=solve_ivp(rhs,(times[0],times[-1]),np.zeros(dimension),t_eval=times,rtol=1e-9,atol=1e-11)
    if not sol.success: raise RuntimeError(sol.message)
    return sol.y.T


def metric_contraction_rate(jacobian, metric):
    """Pointwise rate from J.T M+M J. A domain certificate needs all J in it."""
    J=np.asarray(jacobian); M=np.asarray(metric)
    if not np.allclose(M,M.T) or np.min(np.linalg.eigvalsh(M))<=0:
        raise ValueError('metric must be symmetric positive definite')
    return float(-0.5*np.max(eigvalsh(J.T@M+M@J,M)))


def regional_error_bound(time, contraction, residual_bound, initial_error=0):
    """Metric-norm bound given proven domain-wide constants and invariance.

    Both trajectories must remain in a common convex forward-invariant domain.
    The reduced field contracts there at the supplied positive rate. The full
    minus reduced residual is bounded in that same metric throughout the domain.
    """
    if contraction<=0 or residual_bound<0 or initial_error<0: raise ValueError('invalid bound')
    t=np.asarray(time,dtype=float)
    if np.any(t<0): raise ValueError('time must be nonnegative')
    return initial_error*np.exp(-contraction*t)+residual_bound*(-np.expm1(-contraction*t))/contraction


def phase_chord_error(full, reduced):
    """Instantaneous mean squared chord distance over unordered node pairs."""
    full=np.asarray(full); reduced=np.asarray(reduced)
    if full.shape!=reduced.shape or full.shape[-1]<2: raise ValueError('incompatible phase arrays')
    i,j=np.triu_indices(full.shape[-1],1)
    a=full[...,i]-full[...,j];b=reduced[...,i]-reduced[...,j]
    return np.mean(np.abs(np.exp(1j*a)-np.exp(1j*b))**2,axis=-1)


def cubic_decay_bounds(time, contraction, residual_amplitude):
    """Bounds given ||r(t)||_M <= a exp(-3*lambda*t), same initial state.

    Cubic spatial residuals along exponentially decaying trajectories have
    this form when the corresponding domain-wide constants are established.
    Returns instantaneous metric path bound and time-averaged squared forcing
    bound. Metric-to-phase and coupling normalization factors are separate.
    """
    if contraction<=0 or residual_amplitude<0: raise ValueError('invalid constants')
    t=np.asarray(time,dtype=float)
    if np.any(t<0): raise ValueError('time must be nonnegative')
    lam=contraction; a=residual_amplitude
    path=a/(2*lam)*np.exp(-lam*t)*(-np.expm1(-2*lam*t))
    z=6*lam*t
    factor=np.divide(-np.expm1(-z),z,out=np.ones_like(z),where=z!=0)
    return path,a*a*factor


def response_matching_weights(amplitude, frequency):
    """Sine candidate weights matching the gradient of A*sin(k.x) at zero."""
    return amplitude*np.asarray(frequency,dtype=float)
