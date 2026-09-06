import math
import random

def dominates(a,b):
    no_worse=all(x<=y for x,y in zip(a,b))
    strictly_better=any(x<y for x,y in zip(a,b))
    return no_worse and strictly_better

def calculate_strength(solutions):
    n=len(solutions)
    strength=[0]*n

    for i in range(n):
        for j in range(n):
            if i!=j and dominates(solutions[i],solutions[j]):
                strength[i]+=1

    return strength

def calculate_raw_fitness(solutions,strength):
    n=len(solutions)
    raw_fitness=[0]*n

    for i in range(n):
        for j in range(n):
            if i!=j and dominates(solutions[j],solutions[i]):
                raw_fitness[i]+=strength[j]

    return raw_fitness

def euclidean_distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def calculate_distance_matrix(solutions):
    n=len(solutions)
    distances=[[0.0]*n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i!=j:
                distances[i][j]=euclidean_distance(
                    solutions[i],
                    solutions[j]
                )

    return distances

def kth_nearest_distance(distances,i,k):
    neighbor_distances=[
        distances[i][j]
        for j in range(len(distances))
        if j!=i
    ]

    neighbor_distances.sort()

    return neighbor_distances[k-1]

def calculate_density(distances,k):
    n=len(distances)
    density=[0.0]*n

    for i in range(n):
        sigma_k=kth_nearest_distance(
            distances,
            i,
            k
        )

        density[i]=1.0/(sigma_k+2.0)

    return density

def calculate_fitness(raw_fitness,density):
    n=len(raw_fitness)
    fitness=[0.0]*n

    for i in range(n):
        fitness[i]=raw_fitness[i]+density[i]

    return fitness

def get_sorted_distances(distances,i,active):
    values=[]

    for j in active:
        if i!=j:
            values.append(distances[i][j])

    values.sort()

    return values

def find_truncation_candidate(distances,active):
    best=active[0]
    best_distances=get_sorted_distances(
        distances,
        best,
        active
    )

    for i in active[1:]:
        current_distances=get_sorted_distances(
            distances,
            i,
            active
        )

        if current_distances<best_distances:
            best=i
            best_distances=current_distances

    return best

def truncate_archive(solutions,archive_indices,archive_size):
    active=archive_indices.copy()
    distances=calculate_distance_matrix(solutions)

    while len(active)>archive_size:
        candidate=find_truncation_candidate(
            distances,
            active
        )

        active.remove(candidate)

    return active

def environmental_selection(solutions,fitness,archive_size):
    archive=[
        i
        for i in range(len(solutions))
        if fitness[i]<1
    ]

    if len(archive)>archive_size:
        archive=truncate_archive(
            solutions,
            archive,
            archive_size
        )

    elif len(archive)<archive_size:
        remaining=[
            i
            for i in range(len(solutions))
            if i not in archive
        ]

        remaining.sort(
            key=lambda i: fitness[i]
        )

        needed=archive_size-len(archive)

        archive.extend(
            remaining[:needed]
        )

    return archive

def tournament_selection(archive,fitness):
    a,b=random.sample(archive,2)

    if fitness[a]<fitness[b]:
        return a

    if fitness[b]<fitness[a]:
        return b

    return random.choice([a,b])

def select_parents(archive,fitness,num_parents):
    parents=[]

    for _ in range(num_parents):
        winner=tournament_selection(
            archive,
            fitness
        )

        parents.append(winner)

    return parents

def arithmetic_crossover(parent1,parent2):
    alpha=random.random()

    child=[]

    for x,y in zip(parent1,parent2):
        value=alpha*x+(1-alpha)*y
        child.append(value)

    return child

if __name__=="__main__":

    solutions=[
        [1,8],
        [2,7],
        [3,6],
        [7,3],
        [8,2]
    ]

    strength=calculate_strength(
        solutions
    )

    raw_fitness=calculate_raw_fitness(
        solutions,
        strength
    )

    distances=calculate_distance_matrix(
        solutions
    )

    k=2

    density=calculate_density(
        distances,
        k
    )

    fitness=calculate_fitness(
        raw_fitness,
        density
    )

    archive_size=3

    archive=environmental_selection(
        solutions,
        fitness,
        archive_size
    )

    parents=select_parents(
        archive,
        fitness,
        2
    )

    parent1=solutions[parents[0]]
    parent2=solutions[parents[1]]

    child=arithmetic_crossover(
        parent1,
        parent2
    )

    print()
    print("Archive")
    print("-"*60)

    for i in archive:
        print(
            f"Solution {i}: {solutions[i]}"
        )

    print()

    print("Selected Parents")
    print("-"*60)

    print(
        f"Parent 1: {parent1}"
    )

    print(
        f"Parent 2: {parent2}"
    )

    print()

    print("Child")
    print("-"*60)

    print(child)