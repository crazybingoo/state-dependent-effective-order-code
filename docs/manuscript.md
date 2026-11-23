# Manuscript and code

The accompanying manuscript is **Effective order and dynamical reduction in hypergraphs under different state distributions**.

## Order selection

`methods/projection.py` implements the single-direction Poisson density, its Fourier moments, admissible projection anchors, Gram matrices, residual risks, and the lowest supplied order meeting a tolerance. The coupling and error tolerance remain fixed while the distribution changes.

`methods/hypergraph.py` implements the corresponding centered-product calculation for independent coordinates. Overlapping contributions are combined before their coefficients are squared. The demo constructs its own toy topology rather than loading observations.

## Dynamical reduction

`methods/dynamics.py` separates coupling approximation from autonomous dynamical preservation. It provides variational residual propagation, local response matching, and evaluation of error bounds from supplied contraction and residual constants. These functions do not infer a valid invariant domain merely from sampled trajectories.

## Estimation and uncertainty

`methods/estimation.py` provides weighted projection with an unpenalized intercept and an empirical Bernstein interval for independent bounded losses. Candidate dictionary loss is not the exact risk over the complete function space.

## Examples and tests

`methods/demo.py` creates all inputs in memory. `tests/test_principles.py` checks the mathematical implementations using analytical examples and quadrature. No clinical input, clinical output, or clinical pipeline cache is included. The repository documents reusable components rather than claiming end-to-end reproduction of the clinical study.
