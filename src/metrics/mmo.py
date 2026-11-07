"""Indicators of the CEC 2020 multimodal multi-objective competition.

Ports of the organisers' MATLAB code (`Indicator_calculation/`):

* IGDX  - IGD in decision space (obtained PS vs. reference PS).
* IGDF  - IGD in objective space (obtained PF vs. reference PF).
* CR    - cover rate of the obtained Pareto set.
* PSP   - Pareto Sets Proximity = CR / IGDX.
* HV    - hypervolume w.r.t. the problem's reference point.

The competition reports four values (all smaller-is-better): 1/PSP, 1/HV,
IGDX and IGDF.

Differences from the MATLAB code, for correctness:

* Hypervolume uses this project's exact N-dimensional implementation. The MATLAB
  ``Hypervolume_calculation`` sorts on the first objective and sums 2-D boxes,
  which is only valid for two objectives, yet the suite contains
  three-objective problems.
* IGD is vectorised with NumPy (same formula as ``calculate_igd``).
"""

from typing import Dict

import numpy as np

from .hypervolume import calculate_hypervolume

# Problems whose CR ignores one variable (1-based index) in the MATLAB code.
# The code lists exactly these names; the "_l" variants are *not* included.
CR_IGNORED_DIMENSION = {
    "MMF9": 2, "MMF10": 2, "MMF11": 2, "MMF12": 2, "MMF20": 2,
    "MMF14": 3, "MMF15": 3,
}


def igd(obtained: np.ndarray, reference: np.ndarray) -> float:
    """Mean over reference points of the distance to the nearest obtained point."""
    obtained = np.atleast_2d(np.asarray(obtained, float))
    reference = np.atleast_2d(np.asarray(reference, float))

    if len(obtained) == 0:
        return float("inf")

    best = np.empty(len(reference))

    # chunked to bound memory for large reference sets
    for start in range(0, len(reference), 256):
        chunk = reference[start:start + 256]
        diff = chunk[:, None, :] - obtained[None, :, :]
        best[start:start + 256] = np.sqrt((diff ** 2).sum(axis=2)).min(axis=1)

    return float(best.mean())


def cover_rate(obtained_ps, reference_ps, problem_name: str = "") -> float:
    """CR_calculation.m: how much of the reference PS extent is covered."""
    obtained_ps = np.atleast_2d(np.asarray(obtained_ps, float))
    reference_ps = np.atleast_2d(np.asarray(reference_ps, float))

    n_var = reference_ps.shape[1]
    o_min, o_max = obtained_ps.min(axis=0), obtained_ps.max(axis=0)
    r_min, r_max = reference_ps.min(axis=0), reference_ps.max(axis=0)
    ignored = CR_IGNORED_DIMENSION.get(problem_name)

    kesi = np.empty(n_var)

    for i in range(n_var):
        if r_max[i] == r_min[i] or ignored == i + 1:
            kesi[i] = 1.0
        elif o_min[i] >= r_max[i] or r_min[i] >= o_max[i]:
            kesi[i] = 0.0
        else:
            kesi[i] = (
                (min(o_max[i], r_max[i]) - max(o_min[i], r_min[i]))
                / (r_max[i] - r_min[i])
            ) ** 2

    return float(np.prod(kesi) ** (1.0 / (2 * n_var)))


def nondominated_mask(objectives: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated rows (minimisation)."""
    objectives = np.asarray(objectives, float)
    keep = np.ones(len(objectives), dtype=bool)

    for i in range(len(objectives)):
        dominated = (
            np.all(objectives <= objectives[i], axis=1)
            & np.any(objectives < objectives[i], axis=1)
        )

        if dominated.any():
            keep[i] = False

    return keep


def mmo_indicators(
    ps, pf, reference_ps, reference_pf, hv_reference_point,
    problem_name: str = "",
) -> Dict[str, float]:
    """All competition indicators for one run (``ps``/``pf`` = obtained sets)."""
    ps = np.atleast_2d(np.asarray(ps, float))
    pf = np.atleast_2d(np.asarray(pf, float))

    igdx = igd(ps, reference_ps)
    igdf = igd(pf, reference_pf)
    cr = cover_rate(ps, reference_ps, problem_name)
    hv = calculate_hypervolume(
        [[float(v) for v in row] for row in pf],
        [float(v) for v in hv_reference_point],
    )

    psp = cr / igdx if igdx > 0 else float("inf")

    return {
        "rPSP": 1.0 / psp if psp > 0 else float("inf"),
        "rHV": 1.0 / hv if hv > 0 else float("inf"),
        "IGDX": igdx,
        "IGDF": igdf,
        "CR": cr,
        "PSP": psp,
        "HV": hv,
    }
