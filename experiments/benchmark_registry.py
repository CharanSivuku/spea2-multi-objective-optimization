
"""Central registry for the benchmark experiment suite."""

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

from src.spea2 import zdt1, zdt2, zdt3, zdt4, zdt6

from src.benchmarks.dtlz import (
    DTLZ_FUNCTIONS,
    generate_dtlz_reference_front,
)

from src.benchmarks.classical import (
    binh1, binh1_reference_front,
    deb, deb_reference_front,
    deb2, deb2_reference_front,
    fonseca, fonseca_reference_front,
    fonseca2, fonseca2_reference_front,
    kursawe, kursawe_reference_front,
)

from src.benchmarks import classical_extra as extra


@dataclass(frozen=True)
class Benchmark:
    name: str
    objective: Callable[[Sequence[float]], List[float]]
    n_var: int
    n_obj: int
    lower: Sequence[float]
    upper: Sequence[float]
    reference_front: List[List[float]]
    # Total constraint violation (0 = feasible); None for unconstrained.
    constraint: Optional[Callable[[Sequence[float]], float]] = None


def _zdt_front(name: str, n: int = 1000) -> List[List[float]]:
    import math

    if name in ("ZDT1", "ZDT4"):
        return [
            [i / n, 1.0 - math.sqrt(i / n)]
            for i in range(n + 1)
        ]

    if name == "ZDT2":
        return [
            [i / n, 1.0 - (i / n)**2]
            for i in range(n + 1)
        ]

    if name == "ZDT3":
        intervals = [
            (0.0, 0.0830015349),
            (0.1822287280, 0.2577623634),
            (0.4093136748, 0.4538821041),
            (0.6183967944, 0.6525117038),
            (0.8233317983, 0.8518328654),
        ]

        result = []

        for lo, hi in intervals:
            count = max(2, n // len(intervals))

            for i in range(count):
                f1 = lo + (hi - lo) * i / (count - 1)
                f2 = (
                    1.0 - math.sqrt(f1)
                    - f1 * math.sin(10.0 * math.pi * f1)
                )
                result.append([f1, f2])

        return result

    if name == "ZDT6":
        lo = 0.2807753191

        return [
            [
                lo + (1.0 - lo) * i / n,
                1.0 - (lo + (1.0 - lo) * i / n)**2,
            ]
            for i in range(n + 1)
        ]

    raise ValueError(f"Unknown ZDT benchmark: {name}")


def build_registry(
    dtlz_n_var: int = 12,
    n_obj: int = 3,
    dtlz_divisions: int = 50,
) -> dict[str, Benchmark]:

    registry = {}

    # ZDT
    zdt = {
        "ZDT1": (zdt1, 30),
        "ZDT2": (zdt2, 30),
        "ZDT3": (zdt3, 30),
        "ZDT4": (zdt4, 10),
        "ZDT6": (zdt6, 10),
    }

    for name, (fn, n_var) in zdt.items():
        lower = [0.0] + (
            [-5.0] * (n_var - 1)
            if name == "ZDT4"
            else [0.0] * (n_var - 1)
        )

        upper = [1.0] + (
            [5.0] * (n_var - 1)
            if name == "ZDT4"
            else [1.0] * (n_var - 1)
        )

        registry[name] = Benchmark(
            name, fn, n_var, 2,
            lower, upper, _zdt_front(name)
        )

    # DTLZ
    if dtlz_n_var < n_obj:
        raise ValueError("dtlz_n_var must be >= n_obj")

    for name, fn in DTLZ_FUNCTIONS.items():
        registry[name] = Benchmark(
            name=name,
            objective=lambda x, f=fn, m=n_obj: f(x, n_obj=m),
            n_var=dtlz_n_var,
            n_obj=n_obj,
            lower=[0.0] * dtlz_n_var,
            upper=[1.0] * dtlz_n_var,
            reference_front=generate_dtlz_reference_front(
                name,
                n_obj=n_obj,
                divisions=dtlz_divisions,
            ),
        )

    # Classical
    classical = {
        "Binh1": (
            binh1, 2, 2,
            [-5.0, -5.0], [10.0, 10.0],
            binh1_reference_front(),
        ),
        "Deb": (
            deb, 2, 2,
            [0.0, 0.0], [1.0, 1.0],
            deb_reference_front(),
        ),
        "Deb2": (
            deb2, 2, 2,
            [0.0, 0.0], [1.0, 1.0],
            deb2_reference_front(),
        ),
        "Fonseca": (
            fonseca, 2, 2,
            [-4.0, -4.0], [4.0, 4.0],
            fonseca_reference_front(),
        ),
        "Fonseca2": (
            fonseca2, 2, 2,
            [-4.0, -4.0], [4.0, 4.0],
            fonseca2_reference_front(),
        ),
        "Kursawe": (
            kursawe, 3, 2,
            [-5.0, -5.0, -5.0],
            [5.0, 5.0, 5.0],
            kursawe_reference_front(),
        ),
    }

    for name, data in classical.items():
        fn, n_var, n_obj, lower, upper, reference_front = data

        registry[name] = Benchmark(
            name=name,
            objective=fn,
            n_var=n_var,
            n_obj=n_obj,
            lower=lower,
            upper=upper,
            reference_front=reference_front,
        )

    # Remaining classical benchmarks:
    # name -> (objective, n_var, n_obj, lower, upper, front_fn, constraint)
    extra_problems = {
        "Binh3": (
            extra.binh3, 2, 3,
            extra.BINH3_LOWER, extra.BINH3_UPPER,
            extra.binh3_reference_front, None,
        ),
        "Laumanns": (
            extra.laumanns, 2, 2,
            extra.LAUMANNS_LOWER, extra.LAUMANNS_UPPER,
            extra.laumanns_reference_front, None,
        ),
        "Murata": (
            extra.murata, 2, 2,
            extra.MURATA_LOWER, extra.MURATA_UPPER,
            extra.murata_reference_front, None,
        ),
        "Quagliarella": (
            extra.quagliarella, extra.QUAGLIARELLA_N_VAR, 2,
            extra.QUAGLIARELLA_LOWER, extra.QUAGLIARELLA_UPPER,
            extra.quagliarella_reference_front, None,
        ),
        "Rendon": (
            extra.rendon, 2, 2,
            extra.RENDON_LOWER, extra.RENDON_UPPER,
            extra.rendon_reference_front, None,
        ),
        "Rendon2": (
            extra.rendon2, 2, 2,
            extra.RENDON2_LOWER, extra.RENDON2_UPPER,
            extra.rendon2_reference_front, None,
        ),
        "Schaffer": (
            extra.schaffer, 1, 2,
            extra.SCHAFFER_LOWER, extra.SCHAFFER_UPPER,
            extra.schaffer_reference_front, None,
        ),
        "Schaffer2": (
            extra.schaffer2, 1, 2,
            extra.SCHAFFER2_LOWER, extra.SCHAFFER2_UPPER,
            extra.schaffer2_reference_front, None,
        ),
        "Srinivas": (
            extra.srinivas, 2, 2,
            extra.SRINIVAS_LOWER, extra.SRINIVAS_UPPER,
            extra.srinivas_reference_front, extra.srinivas_violation,
        ),
        "Tanaka": (
            extra.tanaka, 2, 2,
            extra.TANAKA_LOWER, extra.TANAKA_UPPER,
            extra.tanaka_reference_front, extra.tanaka_violation,
        ),
        "Viennet": (
            extra.viennet, 2, 3,
            extra.VIENNET_LOWER, extra.VIENNET_UPPER,
            extra.viennet_reference_front, None,
        ),
        "Viennet2": (
            extra.viennet2, 2, 3,
            extra.VIENNET2_LOWER, extra.VIENNET2_UPPER,
            extra.viennet2_reference_front, None,
        ),
    }

    for name, data in extra_problems.items():
        fn, n_var, n_obj_p, lower, upper, front_fn, constraint = data

        registry[name] = Benchmark(
            name=name,
            objective=fn,
            n_var=n_var,
            n_obj=n_obj_p,
            lower=list(lower),
            upper=list(upper),
            reference_front=front_fn(),
            constraint=constraint,
        )

    return registry
