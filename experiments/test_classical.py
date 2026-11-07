
from experiments.benchmark_registry import build_registry


def test_classical_registry():
    registry = build_registry()

    expected = [
        "Binh1",
        "Deb",
        "Deb2",
        "Fonseca",
        "Fonseca2",
    ]

    for name in expected:
        assert name in registry

        benchmark = registry[name]

        assert benchmark.n_var == 2
        assert benchmark.n_obj == 2
        assert len(benchmark.lower) == 2
        assert len(benchmark.upper) == 2
        assert len(benchmark.reference_front) > 0

        objectives = benchmark.objective(
            [
                (benchmark.lower[0] + benchmark.upper[0]) / 2,
                (benchmark.lower[1] + benchmark.upper[1]) / 2,
            ]
        )

        assert len(objectives) == benchmark.n_obj
        assert all(isinstance(v, (int, float)) for v in objectives)


def test_existing_benchmarks_preserved():
    registry = build_registry()

    for name in [
        "ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6",
        "DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4",
        "DTLZ5", "DTLZ6", "DTLZ7",
    ]:
        assert name in registry
