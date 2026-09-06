import math
import sys
import os
import matplotlib.pyplot as plt

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)

from spea2 import spea2,zdt1

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

results_dir=os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../results/figures"
    )
)

os.makedirs(
    results_dir,
    exist_ok=True
)

plt.savefig(
    os.path.join(
        results_dir,
        "spea2_zdt1.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()