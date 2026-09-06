def dominates(a, b):
    no_worse = all(x <= y for x, y in zip(a, b))
    strictly_better = any(x < y for x, y in zip(a, b))
    return no_worse and strictly_better

def calculate_strength(solutions):
    n = len(solutions)
    strength = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and dominates(solutions[i], solutions[j]):
                strength[i] += 1
    return strength

def calculate_raw_fitness(solutions, strength):
    n = len(solutions)
    raw_fitness = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and dominates(solutions[j], solutions[i]):
                raw_fitness[i] += strength[j]
    return raw_fitness

if __name__ == "__main__":
    solutions = [
        [1, 1],
        [2, 2],
        [3, 3],
        [4, 4]
    ]
    strength = calculate_strength(solutions)
    raw_fitness = calculate_raw_fitness(
        solutions,
        strength
    )
    
    print("SPEA2 Fitness Assignment")
    print("-" * 40)
    for i in range(len(solutions)):
        print(
            f"Solution {i}: "
            f"{solutions[i]}, "
            f"Strength = {strength[i]}, "
            f"Raw Fitness = {raw_fitness[i]}"
        )