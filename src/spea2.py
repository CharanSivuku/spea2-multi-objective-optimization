import math
import random

import numpy as np


def dominates(a, b):
    no_worse = all(x <= y for x, y in zip(a, b))
    strictly_better = any(x < y for x, y in zip(a, b))

    return no_worse and strictly_better


def constraint_dominates(a, violation_a, b, violation_b):
    """Feasibility-first (Deb) constraint dominance for minimisation.

    A violation of 0 means feasible; positive values are the total amount
    by which constraints are violated.

    1. A feasible solution dominates any infeasible solution.
    2. Between two infeasible solutions, the smaller violation dominates.
    3. Between two feasible solutions, ordinary Pareto dominance applies.
    """
    feasible_a = violation_a <= 0.0
    feasible_b = violation_b <= 0.0

    if feasible_a and feasible_b:
        return dominates(a, b)

    if feasible_a:
        return True

    if feasible_b:
        return False

    return violation_a < violation_b


def _dominance_test(solutions, violations):
    """Return f(i, j) -> True if solution i dominates solution j."""
    if violations is None:
        return lambda i, j: dominates(solutions[i], solutions[j])

    if len(violations) != len(solutions):
        raise ValueError(
            "violations must have one entry per solution"
        )

    return lambda i, j: constraint_dominates(
        solutions[i], violations[i],
        solutions[j], violations[j]
    )


def _dominance_matrix(solutions, violations=None):
    """Boolean matrix ``dom[i, j]`` = solution i dominates solution j.

    Vectorised equivalent of the pairwise ``dominates`` /
    ``constraint_dominates`` loops (see the ``*_reference`` functions).
    """
    a = np.asarray(solutions, dtype=float)

    if violations is not None and len(violations) != len(a):
        raise ValueError(
            "violations must have one entry per solution"
        )

    no_worse = (a[:, None, :] <= a[None, :, :]).all(axis=2)
    strictly_better = (a[:, None, :] < a[None, :, :]).any(axis=2)
    pareto = no_worse & strictly_better

    if violations is None:
        dom = pareto
    else:
        v = np.asarray(violations, dtype=float)
        feasible = v <= 0.0
        both_feasible = feasible[:, None] & feasible[None, :]
        both_infeasible = ~feasible[:, None] & ~feasible[None, :]

        dom = (
            (both_feasible & pareto)
            | (feasible[:, None] & ~feasible[None, :])
            | (both_infeasible & (v[:, None] < v[None, :]))
        )

    np.fill_diagonal(dom, False)

    return dom


def calculate_strength(solutions, violations=None):
    dom = _dominance_matrix(solutions, violations)

    return dom.sum(axis=1).tolist()


def calculate_raw_fitness(solutions, strength, violations=None):
    dom = _dominance_matrix(solutions, violations)
    s = np.asarray(strength, dtype=np.int64)

    return (dom * s[:, None]).sum(axis=0).tolist()


def euclidean_distance(a, b):
    return math.sqrt(
        sum((x - y) ** 2 for x, y in zip(a, b))
    )


def calculate_distance_matrix(solutions):
    """Pairwise Euclidean distances as an (n, n) array (zero diagonal)."""
    a = np.asarray(solutions, dtype=float)
    diff = a[:, None, :] - a[None, :, :]
    # np.power (libm pow), not diff ** 2 (which NumPy turns into a
    # multiplication): Python's ``x ** 2`` differs from ``x * x`` in the last
    # bit for ~0.1 % of floats, and this must match ``euclidean_distance``.
    distances = np.sqrt(np.power(diff, 2.0).sum(axis=2))
    np.fill_diagonal(distances, 0.0)

    return distances


def kth_nearest_distance(distances, i, k):
    neighbor_distances = [
        distances[i][j]
        for j in range(len(distances))
        if i != j
    ]

    neighbor_distances.sort()

    return neighbor_distances[k - 1]


def calculate_density(distances, k):
    d = np.array(distances, dtype=float)
    n = len(d)

    if k < 1 or k > n - 1:
        raise IndexError("k must be between 1 and the number of neighbours")

    np.fill_diagonal(d, np.inf)
    sigma_k = np.partition(d, k - 1, axis=1)[:, k - 1]

    return (1.0 / (sigma_k + 2.0)).tolist()


# ---- original pure-Python versions, kept as the specification ----


def calculate_strength_reference(solutions, violations=None):
    n = len(solutions)
    strength = [0] * n
    dominated_by = _dominance_test(solutions, violations)

    for i in range(n):
        for j in range(n):
            if i != j and dominated_by(i, j):
                strength[i] += 1

    return strength


def calculate_raw_fitness_reference(solutions, strength, violations=None):
    n = len(solutions)
    raw_fitness = [0] * n
    dominated_by = _dominance_test(solutions, violations)

    for i in range(n):
        for j in range(n):
            if i != j and dominated_by(j, i):
                raw_fitness[i] += strength[j]

    return raw_fitness


def calculate_distance_matrix_reference(solutions):
    n = len(solutions)
    distances = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                distances[i][j] = euclidean_distance(
                    solutions[i],
                    solutions[j]
                )

    return distances


def calculate_density_reference(distances, k):
    n = len(distances)
    density = [0.0] * n

    for i in range(n):
        sigma_k = kth_nearest_distance(
            distances,
            i,
            k
        )

        density[i] = 1.0 / (sigma_k + 2.0)

    return density


def calculate_fitness(raw_fitness, density):
    n = len(raw_fitness)
    fitness = [0.0] * n

    for i in range(n):
        fitness[i] = raw_fitness[i] + density[i]

    return fitness


def get_sorted_distances(distances, i, active):
    values = []

    for j in active:
        if i != j:
            values.append(distances[i][j])

    values.sort()

    return values


def find_truncation_candidate(distances, active):
    best = active[0]

    best_distances = get_sorted_distances(
        distances,
        best,
        active
    )

    for i in active[1:]:
        current_distances = get_sorted_distances(
            distances,
            i,
            active
        )

        if current_distances < best_distances:
            best = i
            best_distances = current_distances

    return best


def truncate_archive_reference(objectives, archive_indices, archive_size):
    """Original (slow) truncation, kept as the specification of the result.

    Repeatedly removes the solution whose sorted list of distances to the
    other remaining solutions is lexicographically smallest (ties: the
    earliest in archive order).
    """
    active = archive_indices.copy()
    distances = calculate_distance_matrix(objectives)

    while len(active) > archive_size:
        candidate = find_truncation_candidate(
            distances,
            active
        )

        active.remove(candidate)

    return active


def truncate_archive(objectives, archive_indices, archive_size):
    """Fast truncation producing exactly the same removals as
    ``truncate_archive_reference``.

    Only the nearest-neighbour distance is needed to find the candidates for
    removal (the lexicographic minimum must have the smallest first element);
    the full sorted rows are compared only among candidates tied on it, which
    happens for at least a mutual nearest-neighbour pair on every step. The
    nearest-neighbour table is updated only for rows that pointed at the
    removed solution.
    """
    active = archive_indices.copy()

    if len(active) <= archive_size:
        return active

    points = np.asarray([objectives[i] for i in active], dtype=float)
    n = len(active)

    diff = points[:, None, :] - points[None, :, :]
    distance = np.sqrt(np.power(diff, 2.0).sum(axis=2))  # same bits as Python's ** 2
    np.fill_diagonal(distance, np.inf)

    rows = np.arange(n)
    nearest_index = distance.argmin(axis=1)
    nearest = distance[rows, nearest_index]

    removed = np.zeros(n, dtype=bool)
    remaining = n

    while remaining > archive_size:
        masked = np.where(removed, np.inf, nearest)
        smallest = masked.min()
        candidates = np.flatnonzero(masked == smallest)

        if len(candidates) == 1:
            victim = int(candidates[0])
        else:
            victim = None
            victim_list = None

            for c in candidates:
                # removed solutions and the solution itself are +inf and sort last
                current = tuple(np.sort(distance[c])[:remaining - 1].tolist())

                if victim is None or current < victim_list:
                    victim = int(c)
                    victim_list = current

        removed[victim] = True
        distance[victim, :] = np.inf
        distance[:, victim] = np.inf
        remaining -= 1

        for r in np.flatnonzero((nearest_index == victim) & ~removed):
            nearest_index[r] = distance[r].argmin()
            nearest[r] = distance[r, nearest_index[r]]

    return [active[p] for p in range(n) if not removed[p]]


def environmental_selection(objectives, fitness, archive_size):
    archive = [
        i
        for i in range(len(objectives))
        if fitness[i] < 1
    ]

    if len(archive) > archive_size:

        archive = truncate_archive(
            objectives,
            archive,
            archive_size
        )

    elif len(archive) < archive_size:

        remaining = [
            i
            for i in range(len(objectives))
            if i not in archive
        ]

        remaining.sort(
            key=lambda i: fitness[i]
        )

        needed = archive_size - len(archive)

        archive.extend(
            remaining[:needed]
        )

    return archive


def tournament_selection(fitness):
    a, b = random.sample(
        range(len(fitness)),
        2
    )

    if fitness[a] < fitness[b]:
        return a

    if fitness[b] < fitness[a]:
        return b

    return random.choice([a, b])


def select_parents(fitness, num_parents):
    parents = []

    for _ in range(num_parents):
        winner = tournament_selection(
            fitness
        )

        parents.append(winner)

    return parents


def sbx_crossover(
    parent1,
    parent2,
    lower_bound,
    upper_bound,
    eta_c=20,
    crossover_probability=0.9
):
    child1 = []
    child2 = []

    if isinstance(lower_bound, (int, float)):
        lower_bounds = [lower_bound] * len(parent1)
    else:
        lower_bounds = lower_bound

    if isinstance(upper_bound, (int, float)):
        upper_bounds = [upper_bound] * len(parent1)
    else:
        upper_bounds = upper_bound

    for i, (x1, x2) in enumerate(zip(parent1, parent2)):

        y1 = lower_bounds[i]
        y2 = upper_bounds[i]

        if random.random() > crossover_probability:
            child1.append(x1)
            child2.append(x2)
            continue

        if abs(x1 - x2) < 1e-14:
            child1.append(x1)
            child2.append(x2)
            continue

        if x1 > x2:
            x1, x2 = x2, x1

        u = random.random()

        beta = 1.0 + 2.0 * (x1 - y1) / (x2 - x1)
        alpha = 2.0 - beta ** (-(eta_c + 1.0))

        if u <= 1.0 / alpha:
            beta_q = (u * alpha) ** (
                1.0 / (eta_c + 1.0)
            )
        else:
            beta_q = (1.0 / (
                2.0 - u * alpha
            )) ** (
                1.0 / (eta_c + 1.0)
            )

        c1 = 0.5 * (
            (x1 + x2)
            - beta_q * (x2 - x1)
        )

        beta = 1.0 + 2.0 * (y2 - x2) / (x2 - x1)
        alpha = 2.0 - beta ** (-(eta_c + 1.0))

        if u <= 1.0 / alpha:
            beta_q = (u * alpha) ** (
                1.0 / (eta_c + 1.0)
            )
        else:
            beta_q = (1.0 / (
                2.0 - u * alpha
            )) ** (
                1.0 / (eta_c + 1.0)
            )

        c2 = 0.5 * (
            (x1 + x2)
            + beta_q * (x2 - x1)
        )

        c1 = max(
            y1,
            min(y2, c1)
        )

        c2 = max(
            y1,
            min(y2, c2)
        )

        if random.random() <= 0.5:
            child1.append(c2)
            child2.append(c1)
        else:
            child1.append(c1)
            child2.append(c2)

    return child1, child2


def polynomial_mutation(
    solution,
    lower_bound,
    upper_bound,
    mutation_probability,
    eta_m=20
):
    mutated = solution.copy()

    if isinstance(lower_bound, (int, float)):
        lower_bounds = [lower_bound] * len(mutated)
    else:
        lower_bounds = lower_bound

    if isinstance(upper_bound, (int, float)):
        upper_bounds = [upper_bound] * len(mutated)
    else:
        upper_bounds = upper_bound

    for i in range(len(mutated)):

        if random.random() > mutation_probability:
            continue

        x = mutated[i]

        lower = lower_bounds[i]
        upper = upper_bounds[i]

        if upper - lower <= 0:
            continue

        u = random.random()

        delta1 = (
            (x - lower)
            / (upper - lower)
        )

        delta2 = (
            (upper - x)
            / (upper - lower)
        )

        if u <= 0.5:

            xy = 1.0 - delta1

            val = (
                2.0 * u
                + (1.0 - 2.0 * u)
                * (xy ** (eta_m + 1.0))
            )

            delta_q = (
                val ** (1.0 / (eta_m + 1.0))
                - 1.0
            )

        else:

            xy = 1.0 - delta2

            val = (
                2.0 * (1.0 - u)
                + (2.0 * u - 1.0)
                * (xy ** (eta_m + 1.0))
            )

            delta_q = (
                1.0
                - val ** (1.0 / (eta_m + 1.0))
            )

        x = x + delta_q * (upper - lower)

        x = max(
            lower,
            min(upper, x)
        )

        mutated[i] = x

    return mutated


def zdt1(x):
    n = len(x)

    f1 = x[0]

    g = 1.0 + 9.0 * sum(x[1:]) / (n - 1)

    f2 = g * (
        1.0 - math.sqrt(f1 / g)
    )

    return [f1, f2]


def zdt2(solution):
    f1 = solution[0]

    g = (
        1.0
        + 9.0 * sum(solution[1:])
        / (len(solution) - 1)
    )

    f2 = g * (
        1.0 - (f1 / g) ** 2
    )

    return [f1, f2]


def zdt3(solution):
    f1 = solution[0]

    g = (
        1.0
        + 9.0 * sum(solution[1:])
        / (len(solution) - 1)
    )

    f2 = g * (
        1.0
        - math.sqrt(f1 / g)
        - (f1 / g)
        * math.sin(10.0 * math.pi * f1)
    )

    return [f1, f2]


def zdt4(solution):
    f1 = solution[0]

    g = (
        1.0
        + 10.0 * (len(solution) - 1)
        + sum(
            x ** 2
            - 10.0 * math.cos(4.0 * math.pi * x)
            for x in solution[1:]
        )
    )

    f2 = g * (
        1.0 - math.sqrt(f1 / g)
    )

    return [f1, f2]


def zdt6(solution):
    f1 = (
        1.0
        - math.exp(-4.0 * solution[0])
        * math.sin(6.0 * math.pi * solution[0]) ** 6
    )

    g = (
        1.0
        + 9.0
        * (
            sum(solution[1:])
            / (len(solution) - 1)
        ) ** 0.25
    )

    f2 = g * (
        1.0 - (f1 / g) ** 2
    )

    return [f1, f2]


def initialize_population(
    population_size,
    num_variables,
    lower_bound,
    upper_bound
):
    population = []

    if isinstance(lower_bound, (int, float)):
        lower_bounds = [lower_bound] * num_variables
    else:
        lower_bounds = lower_bound

    if isinstance(upper_bound, (int, float)):
        upper_bounds = [upper_bound] * num_variables
    else:
        upper_bounds = upper_bound

    for _ in range(population_size):

        solution = [
            random.uniform(
                lower_bounds[i],
                upper_bounds[i]
            )
            for i in range(num_variables)
        ]

        population.append(solution)

    return population


def create_offspring(
    archive_population,
    archive_fitness,
    population_size,
    lower_bound,
    upper_bound
):
    offspring = []

    mutation_probability = (
        1.0 / len(archive_population[0])
    )

    while len(offspring) < population_size:

        parent_indices = select_parents(
            archive_fitness,
            2
        )

        parent1 = archive_population[
            parent_indices[0]
        ]

        parent2 = archive_population[
            parent_indices[1]
        ]

        child1, child2 = sbx_crossover(
            parent1,
            parent2,
            lower_bound,
            upper_bound
        )

        child1 = polynomial_mutation(
            child1,
            lower_bound,
            upper_bound,
            mutation_probability
        )

        child2 = polynomial_mutation(
            child2,
            lower_bound,
            upper_bound,
            mutation_probability
        )

        offspring.append(child1)

        if len(offspring) < population_size:
            offspring.append(child2)

    return offspring


def spea2(
    population_size,
    num_variables,
    archive_size,
    generations,
    lower_bound,
    upper_bound,
    objective_function=zdt1,
    constraint_function=None
):
    """Run SPEA2.

    constraint_function, if given, maps a decision vector to its total
    constraint violation (0 = feasible, > 0 = infeasible). When it is
    None the algorithm behaves exactly as the original unconstrained SPEA2.
    """
    population = initialize_population(
        population_size,
        num_variables,
        lower_bound,
        upper_bound
    )

    archive = []

    # Objective values (and violations) of the archive are kept between
    # generations instead of being recomputed. The functions are
    # deterministic, so results are identical to re-evaluating them, but each
    # solution is now evaluated exactly once, which makes evaluation-budget
    # accounting exact and halves the evaluation cost.
    archive_objectives = []
    archive_violations = []

    for generation in range(generations):

        combined_population = population + archive

        combined_objectives = [
            objective_function(solution)
            for solution in population
        ] + archive_objectives

        if constraint_function is None:
            violations = None
        else:
            violations = [
                constraint_function(solution)
                for solution in population
            ] + archive_violations

        strength = calculate_strength(
            combined_objectives,
            violations
        )

        raw_fitness = calculate_raw_fitness(
            combined_objectives,
            strength,
            violations
        )

        distances = calculate_distance_matrix(
            combined_objectives
        )

        k = max(
            1,
            int(math.sqrt(
                len(combined_objectives)
            ))
        )

        density = calculate_density(
            distances,
            k
        )

        fitness = calculate_fitness(
            raw_fitness,
            density
        )

        archive_indices = environmental_selection(
            combined_objectives,
            fitness,
            archive_size
        )

        archive = [
            combined_population[i]
            for i in archive_indices
        ]

        archive_objectives = [
            combined_objectives[i]
            for i in archive_indices
        ]

        if violations is not None:
            archive_violations = [
                violations[i]
                for i in archive_indices
            ]

        archive_fitness = [
            fitness[i]
            for i in archive_indices
        ]

        population = create_offspring(
            archive,
            archive_fitness,
            population_size,
            lower_bound,
            upper_bound
        )

    return population, archive