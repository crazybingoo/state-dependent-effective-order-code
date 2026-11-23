# Method implementation guide

## Order and risk

For source phases relative to a receiver, order `q` permits functions of at most `q-1` source coordinates. Order one is constant. The target coupling and tolerance remain fixed when comparing distributions. `effective_order` selects the first supplied risk meeting the tolerance.

| Methods topic | Entry points |
|---|---|
| Fourier representation and Poisson density | `projection.poisson_density`, `moment`, `sine_coefficients` |
| Complete-space weighted projection | `projection.anchors`, `gram`, `project_fourier` |
| Poisson bridge residual matrix | `projection.bridge_residual` |
| Finite-dictionary candidate projection | `estimation.weighted_projection` |
| Residual and variational propagation | `dynamics.linear_error`, `variational_error` |
| Response matching | `dynamics.response_matching_weights` |
| Metric contraction and regional path bounds | `dynamics.metric_contraction_rate`, `regional_error_bound` |
| Pairwise phase-chord error | `dynamics.phase_chord_error` |
| Product-law projection on a hypergraph | `hypergraph.centered_coefficients`, `product_law_risk` |
| Bounded-loss uncertainty | `estimation.empirical_bernstein` |

## Poisson projection

The density is relative to normalized uniform probability on the torus:

`p(x) = (1-rho^2)/(1-2*rho*cos(m.x-phi)+rho^2)`, with integer nonzero `m` and `0 <= rho < 1`.

The Fourier convention is `F(x)=sum_k c[k] exp(i k.x)`. Its characteristic moment is zero unless `k=t*m` for an integer `t`, in which case it is `rho^abs(t) exp(i*t*phi)`. The Gram matrix entry is `G[u,v]=E exp(i*(v-u).X)`.

The code enumerates integer coordinate cancellations on each target orbit and retains frequencies with at most `q-1` nonzero coordinates. Contributions from zero entries of `m` remain fixed. If `B` indexes target frequencies and `T` indexes anchors, the projection solves `G_TT a=G_TB c`. Risk is `c* (G_BB-G_BT G_TT^-1 G_TB) c`. Cross terms are retained. For finite Fourier targets and `rho<1`, these anchors determine the complete-space projection. The plotted endpoint at `rho=1` is a limit, not a density accepted by the solver.

`bridge_residual` evaluates a single residual covariance entry using a Schur complement. Real sine couplings must include both positive and negative frequencies, which `sine_coefficients` supplies.

## Residual propagation and replacement

With error `e=z_reduced-z_full` and residual `r=f-g`, the local error equation is `e'=Dg(z_full)e-r+O(||e||^2)`. The sign of the forcing is therefore negative. `linear_error` evaluates this equation exactly for constant coefficients; `variational_error` uses supplied time-dependent coefficients along a reference trajectory and optionally a quadratic Taylor term.

`response_matching_weights(A,k)` returns pairwise sine weights `A*k`, matching the gradient of `A*sin(k.x)` at synchrony. This matches a local response; a trajectory guarantee additionally requires residual control and domain conditions.

For a common metric `M`, `metric_contraction_rate` computes the contraction rate for a supplied Jacobian. A global regional certificate requires the inequality throughout a common forward-invariant domain. Given a proven positive rate `lambda` and uniform metric residual bound `delta`, `regional_error_bound` evaluates

`||e(t)||_M <= exp(-lambda*t)||e(0)||_M + delta*(1-exp(-lambda*t))/lambda`.

The function evaluates the bound from supplied constants; it does not infer domain invariance from sample trajectories. For a cubic spatial residual on decaying trajectories, `cubic_decay_bounds` uses `||r(t)||_M <= a exp(-3*lambda*t)` to give the sharper path bound `a[exp(-lambda*t)-exp(-3*lambda*t)]/(2*lambda)` and the time-averaged squared-residual bound `a^2[1-exp(-6*lambda*T)]/(6*lambda*T)`. Metric-to-phase conversion and the coupling reference scale must be applied separately.

## Hypergraph product law

The controlled coupling is `F_i=(1-x_i) sum_{e contains i} (|e|-1)! product_{j in e excluding i} x_j`. For independent coordinates of mean `mu` and variance `v`, expansion in centered source products gives coefficients `A_i,S`. Contributions of overlapping hyperedges are combined before squaring. The risk is

`[(1-mu)^2+v] sum_{|S|>=q} A_i,S^2 v^|S|`.

The receiver factor is retained at every order. For `Beta(a,a)`, `mu=1/2` and `v=1/[4(2a+1)]`. The implementation returns receiver-specific risks; a network risk is their arithmetic mean. `evaluate_projection` takes zero-based array indices. The included example uses an explicitly constructed toy topology.

## Finite-dictionary estimation and uncertainty

`weighted_projection` fits a fixed target with weighted centering, scaling and an unpenalized intercept. Its returned sample loss is a candidate loss, not an exact complete-space risk. Training and evaluation arrays should remain separate in applications.

For independent losses bounded by `D`, `empirical_bernstein` uses radius `sqrt(2*s^2*log(2/delta)/n)+7*D*log(2/delta)/(3*(n-1))`, then clips the interval to `[0,D]`. Here `s^2` is the unbiased sample variance. An antithetic pair is averaged before being treated as one independent unit.
