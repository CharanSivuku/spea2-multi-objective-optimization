import math
import random
import matplotlib.pyplot as plt

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
    return math.sqrt(
        sum((x-y)**2 for x,y in zip(a,b))
    )

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
        if i!=j
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

def truncate_archive(objectives,archive_indices,archive_size):
    active=archive_indices.copy()
    distances=calculate_distance_matrix(objectives)

    while len(active)>archive_size:
        candidate=find_truncation_candidate(
            distances,
            active
        )

        active.remove(candidate)

    return active

def environmental_selection(objectives,fitness,archive_size):
    archive=[
        i
        for i in range(len(objectives))
        if fitness[i]<1
    ]

    if len(archive)>archive_size:
        archive=truncate_archive(
            objectives,
            archive,
            archive_size
        )

    elif len(archive)<archive_size:
        remaining=[
            i
            for i in range(len(objectives))
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

def tournament_selection(fitness):
    a,b=random.sample(
        range(len(fitness)),
        2
    )

    if fitness[a]<fitness[b]:
        return a

    if fitness[b]<fitness[a]:
        return b

    return random.choice([a,b])

def select_parents(fitness,num_parents):
    parents=[]

    for _ in range(num_parents):
        winner=tournament_selection(
            fitness
        )

        parents.append(winner)

    return parents

def sbx_crossover(
    parent1,
    parent2,
    lower_bound,
    upper_bound,
    eta_c=20
):
    child1=[]
    child2=[]

    for x1,x2 in zip(parent1,parent2):

        if random.random()>0.5:
            child1.append(x1)
            child2.append(x2)
            continue

        if abs(x1-x2)<1e-14:
            child1.append(x1)
            child2.append(x2)
            continue

        if x1>x2:
            x1,x2=x2,x1

        y1=lower_bound
        y2=upper_bound

        u=random.random()

        beta=1.0+2.0*(x1-y1)/(x2-x1)
        alpha=2.0-beta**(-(eta_c+1.0))

        if u<=1.0/alpha:
            beta_q=(u*alpha)**(
                1.0/(eta_c+1.0)
            )
        else:
            beta_q=(1.0/(2.0-u*alpha))**(
                1.0/(eta_c+1.0)
            )

        c1=0.5*(
            (x1+x2)-beta_q*(x2-x1)
        )

        beta=1.0+2.0*(y2-x2)/(x2-x1)
        alpha=2.0-beta**(-(eta_c+1.0))

        if u<=1.0/alpha:
            beta_q=(u*alpha)**(
                1.0/(eta_c+1.0)
            )
        else:
            beta_q=(1.0/(2.0-u*alpha))**(
                1.0/(eta_c+1.0)
            )

        c2=0.5*(
            (x1+x2)+beta_q*(x2-x1)
        )

        c1=max(
            lower_bound,
            min(upper_bound,c1)
        )

        c2=max(
            lower_bound,
            min(upper_bound,c2)
        )

        if random.random()<=0.5:
            child1.append(c2)
            child2.append(c1)
        else:
            child1.append(c1)
            child2.append(c2)

    return child1,child2

def polynomial_mutation(
    solution,
    lower_bound,
    upper_bound,
    mutation_probability,
    eta_m=20
):
    mutated=solution.copy()

    for i in range(len(mutated)):

        if random.random()>mutation_probability:
            continue

        x=mutated[i]

        if upper_bound-lower_bound<=0:
            continue

        u=random.random()

        delta1=(
            x-lower_bound
        )/(upper_bound-lower_bound)

        delta2=(
            upper_bound-x
        )/(upper_bound-lower_bound)

        if u<=0.5:

            xy=1.0-delta1

            val=(
                2.0*u+
                (1.0-2.0*u)*
                (xy**(eta_m+1.0))
            )

            delta_q=(
                val**(1.0/(eta_m+1.0))-1.0
            )

        else:

            xy=1.0-delta2

            val=(
                2.0*(1.0-u)+
                (2.0*u-1.0)*
                (xy**(eta_m+1.0))
            )

            delta_q=(
                1.0-
                val**(1.0/(eta_m+1.0))
            )

        x=x+delta_q*(
            upper_bound-lower_bound
        )

        x=max(
            lower_bound,
            min(upper_bound,x)
        )

        mutated[i]=x

    return mutated

def zdt1(x):
    n=len(x)

    f1=x[0]

    g=1.0+9.0*sum(x[1:])/(n-1)

    f2=g*(
        1.0-math.sqrt(f1/g)
    )

    return [f1,f2]

def initialize_population(
    population_size,
    num_variables
):
    population=[]

    for _ in range(population_size):

        solution=[
            random.uniform(0.0,1.0)
            for _ in range(num_variables)
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
    offspring=[]

    mutation_probability=1.0/len(
        archive_population[0]
    )

    while len(offspring)<population_size:

        parent_indices=select_parents(
            archive_fitness,
            2
        )

        parent1=archive_population[
            parent_indices[0]
        ]

        parent2=archive_population[
            parent_indices[1]
        ]

        child1,child2=sbx_crossover(
            parent1,
            parent2,
            lower_bound,
            upper_bound
        )

        child1=polynomial_mutation(
            child1,
            lower_bound,
            upper_bound,
            mutation_probability
        )

        child2=polynomial_mutation(
            child2,
            lower_bound,
            upper_bound,
            mutation_probability
        )

        offspring.append(child1)

        if len(offspring)<population_size:
            offspring.append(child2)

    return offspring

def spea2(
    population_size,
    num_variables,
    archive_size,
    generations,
    lower_bound,
    upper_bound
):
    population=initialize_population(
        population_size,
        num_variables
    )

    archive=[]

    for generation in range(generations):

        combined_population=population+archive

        combined_objectives=[
            zdt1(solution)
            for solution in combined_population
        ]

        strength=calculate_strength(
            combined_objectives
        )

        raw_fitness=calculate_raw_fitness(
            combined_objectives,
            strength
        )

        distances=calculate_distance_matrix(
            combined_objectives
        )

        k=max(
            1,
            int(math.sqrt(
                len(combined_objectives)
            ))
        )

        density=calculate_density(
            distances,
            k
        )

        fitness=calculate_fitness(
            raw_fitness,
            density
        )

        archive_indices=environmental_selection(
            combined_objectives,
            fitness,
            archive_size
        )

        archive=[
            combined_population[i]
            for i in archive_indices
        ]

        archive_fitness=[
            fitness[i]
            for i in archive_indices
        ]

        population=create_offspring(
            archive,
            archive_fitness,
            population_size,
            lower_bound,
            upper_bound
        )

        print(
            f"Generation {generation+1}: "
            f"Archive Size = {len(archive)}"
        )

    return population,archive

if __name__=="__main__":

    population_size=100
    num_variables=30
    archive_size=100
    generations=250

    lower_bound=0.0
    upper_bound=1.0

    population,archive=spea2(
        population_size,
        num_variables,
        archive_size,
        generations,
        lower_bound,
        upper_bound
    )

    objectives=[
        zdt1(solution)
        for solution in archive
    ]

    obtained_f1=[
        objective[0]
        for objective in objectives
    ]

    obtained_f2=[
        objective[1]
        for objective in objectives
    ]

    true_f1=[
        i/1000
        for i in range(1001)
    ]

    true_f2=[
        1-math.sqrt(f1)
        for f1 in true_f1
    ]

    plt.scatter(
        obtained_f1,
        obtained_f2,
        label="SPEA2"
    )

    plt.plot(
        true_f1,
        true_f2,
        label="True Pareto Front"
    )

    plt.xlabel("f1")
    plt.ylabel("f2")
    plt.title("SPEA2 on ZDT1")
    plt.legend()
    plt.grid()
    plt.show()