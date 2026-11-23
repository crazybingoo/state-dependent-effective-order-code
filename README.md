# Effective order and dynamical reduction in hypergraphs under different state distributions

Mathematical methods, runnable synthetic examples, and reviewed experimental result tables accompanying the manuscript of the same title.

For a fixed coupling, the state distribution changes the approximation error assigned to each interaction order. The code implements Fourier projection for a Poisson family, projection under independent product distributions, residual propagation, and bounds based on contraction. The examples use analytical functions and a small topology constructed directly in code.

## Contents

| Path | Purpose |
|---|---|
| [methods/projection.py](methods/projection.py) | Fourier moments, admissible anchors, exact projection risks, and order selection |
| [methods/hypergraph.py](methods/hypergraph.py) | Centered-product projection for a prescribed hypergraph coupling |
| [methods/dynamics.py](methods/dynamics.py) | Residual propagation, local response matching, contraction rates, and trajectory bounds |
| [methods/estimation.py](methods/estimation.py) | Weighted finite-dictionary projection and bounded-loss intervals |
| [methods/demo.py](methods/demo.py) | Small deterministic examples generated entirely in memory |
| [tests/](tests/) | Numerical consistency checks and release-policy tests |
| [docs/methods.md](docs/methods.md) | Mathematical conventions and function assumptions |
| [docs/manuscript.md](docs/manuscript.md) | Connection between manuscript topics and code |
| [results/](results/) | Selected SEEG experimental statistics with P/S study labels |
| [docs/results.md](docs/results.md) | Result-table definitions, coverage, and privacy boundaries |

## Run

Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
python -m methods.demo
python -m unittest discover -s tests -v
python tools/check_release.py --history
```

The demo and numerical tests require no input files, network connection, clinical observations, or saved model parameters. They check mathematical components; they do not reproduce the manuscript's clinical analysis or every study-scale experiment.

## Scope of this repository

This repository contains source code, documentation, and reviewed experimental statistics. In result tables, P labels identify study participants and S labels identify records; no connection to real identities is supplied. Receiver indices are numerical study indices, not anatomical or electrode labels. See the [result guide](docs/results.md) and [publication policy](PRIVACY.md).

SEEG recordings, signal segments, clinical records, identifying information, identity lookup tables, electrode locations, and fitted clinical model parameters are not distributed. P/S labels are pseudonyms, not a guarantee of anonymity by themselves; the released fields are limited to experimental outcomes.

The manuscript contains the scientific results and Methods. The repository does not depend on a separate information document. Code examples use synthetic inputs; only the explicitly reviewed result tables belong in version control.

## Validation

The numerical tests compare projection against analytical expressions and independent quadrature, check the residual-forcing sign, verify contraction-bound evaluations, and exercise weighted projection. The [release check](tools/check_release.py) restricts tracked paths, checks result schemas and cell types, and scans committed text including reachable history. Automated checks complement manual review; they cannot establish that arbitrary numerical constants are free of sensitive provenance.
