"""Complete-space Fourier projection under a single-direction Poisson law.

The density is relative to normalized Haar measure on the d-torus.
Fourier coefficients use F(x) = sum_k c[k] exp(i k.x).
"""
import numpy as np


def _direction(m):
    raw = np.asarray(m)
    if raw.ndim != 1 or not len(raw) or not np.all(raw == raw.astype(int)):
        raise ValueError('m must be an integer vector')
    m = raw.astype(int)
    if not np.any(m):
        raise ValueError('m must be nonzero')
    return m


def poisson_density(x, m, rho, phi=0.0):
    """Density relative to uniform probability measure, not Lebesgue measure."""
    m = _direction(m)
    if not 0 <= rho < 1:
        raise ValueError('rho must lie in [0, 1)')
    theta = np.asarray(x) @ m - phi
    return (1-rho*rho)/(1-2*rho*np.cos(theta)+rho*rho)


def integer_shift(k, m):
    """Return t if k=t*m, otherwise None; zero entries of m are respected."""
    k = np.asarray(k, dtype=int)
    j = np.flatnonzero(m)[0]
    if k[j] % int(m[j]):
        return None
    t = int(k[j]//m[j])
    return t if np.array_equal(k, t*m) else None


def moment(k, m, rho, phi=0.0):
    """E exp(i k.X)."""
    t = integer_shift(k, _direction(m))
    return 0j if t is None else rho**abs(t)*np.exp(1j*t*phi)


def anchors(k, m, q):
    """All admissible frequencies on k+Z*m for q<=d; q counts the receiver."""
    m = _direction(m); k = np.asarray(k, dtype=int)
    if not 1 <= q <= len(m):
        raise ValueError('anchor enumeration requires 1<=q<=number of sources')
    # If every orbit frequency is admissible, the target itself suffices.
    if np.count_nonzero(m) + np.count_nonzero(k[m == 0]) <= q-1:
        return {tuple(k)}
    shifts = {-int(k[j])//int(m[j]) for j in np.flatnonzero(m)
              if int(k[j]) % int(m[j]) == 0}
    return {tuple(k+s*m) for s in shifts if np.count_nonzero(k+s*m) <= q-1}


def gram(left, right, m, rho, phi=0.0):
    return np.asarray([[moment(np.asarray(v)-u, m, rho, phi)
                        for v in right] for u in left], dtype=complex)


def project_fourier(coefficients, m, rho, q, phi=0.0):
    """Return exact low-order coefficients and squared L2(P) residual risk.

    Every target orbit contributes all its low-order anchors. Frequencies on
    other orbits are orthogonal to the target. This makes the finite solve an
    exact complete-space projection for finite Fourier targets, with rho<1.
    """
    m = _direction(m)
    if not 0 <= rho < 1 or not isinstance(q, (int, np.integer)) or not 1 <= q <= len(m)+1:
        raise ValueError('require rho in [0,1) and integer q in [1,d+1]')
    if any(len(k) != len(m) or any(v != int(v) for v in k) for k in coefficients):
        raise ValueError('frequency vectors must be integer and match m')
    coeff = {tuple(map(int,k)): complex(v) for k,v in coefficients.items() if v != 0}
    if not coeff: return {}, 0.0
    if q == len(m)+1: return coeff.copy(), 0.0
    K = sorted(coeff); c = np.array([coeff[k] for k in K])
    T = sorted(set().union(*(anchors(k,m,q) for k in K)))
    G = gram(K,K,m,rho,phi)
    energy = float(np.vdot(c,G@c).real)
    if not T: return {}, energy
    A = gram(T,T,m,rho,phi); B = gram(T,K,m,rho,phi)
    a = np.linalg.solve(A,B@c)
    risk = float(np.vdot(c,(G-B.conj().T@np.linalg.solve(A,B))@c).real)
    if risk < -1e-9*max(1,energy):
        raise ArithmeticError('negative risk: inspect conditioning')
    return dict(zip(T,a)), max(0.0,risk)


def sine_coefficients(terms):
    """terms = [(amplitude, integer_frequency, phase), ...]."""
    out = {}
    for amplitude, k, phase in terms:
        k = tuple(k); neg = tuple(-v for v in k)
        out[k] = out.get(k,0)+amplitude*np.exp(1j*phase)/(2j)
        out[neg] = out.get(neg,0)-amplitude*np.exp(-1j*phase)/(2j)
    return out


def evaluate(coefficients, x):
    x = np.asarray(x)
    return sum((c*np.exp(1j*(x@np.asarray(k))) for k,c in coefficients.items()),
               np.zeros(x.shape[:-1],dtype=complex))


def effective_order(risks, epsilon):
    """Smallest supplied order with risk<=epsilon, or None if none qualifies."""
    if epsilon < 0: raise ValueError('epsilon must be nonnegative')
    return next((q for q,r in sorted(risks.items()) if r <= epsilon),None)


def bridge_residual(s, t, anchor_indices, rho):
    """Residual Gram entry after conditioning on anchors on one orbit."""
    if not 0 <= rho < 1: raise ValueError('rho must lie in [0,1)')
    a = np.unique(np.asarray(anchor_indices,dtype=int))
    if len(a)==0: return rho**abs(s-t)
    G = rho**np.abs(a[:,None]-a[None,:])
    return float(rho**abs(s-t)-(rho**np.abs(s-a))@np.linalg.solve(G,rho**np.abs(a-t)))
