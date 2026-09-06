import math
import sys
import os

import matplotlib.pyplot as plt

from src.metrics.igd import calculate_igd
from src.metrics.gd import calculate_gd
from src.metrics.hypervolume import calculate_hypervolume
from src.metrics.spacing import calculate_spacing

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)

from spea2 import spea2, zdt1

population_size = 100
num_variables = 30
archive_size = 100
generations = 250

lower_bound = 0.0
upper_bound = 1.0



population, archive = spea2(
    population_size,
    num_variables,
    archive_size,
    generations,
    lower_bound,
    upper_bound
)

objectives = [
    zdt1(solution)
    for solution in archive
]

reference_front = [
    [
        i / 1000,
        1 - math.sqrt(i / 1000)
    ]
    for i in range(1001)
]

igd = calculate_igd(
    objectives,
    reference_front
)

gd = calculate_gd(
    objectives,
    reference_front
)

hv = calculate_hypervolume(
    objectives,
    [1.1, 1.1]
)

spacing = calculate_spacing(
    objectives
)

print(f"IGD: {igd}")
print(f"GD: {gd}")
print(f"Hypervolume: {hv}")
print(f"Spacing: {spacing}")

metrics_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../results/metrics"
    )
)

os.makedirs(
    metrics_dir,
    exist_ok=True
)

metrics_file = os.path.join(
    metrics_dir,
    "zdt1_metrics.txt"
)

with open(metrics_file, "w") as file:
    file.write(f"IGD: {igd}\n")
    file.write(f"GD: {gd}\n")
    file.write(f"Hypervolume: {hv}\n")
    file.write(f"Spacing: {spacing}\n")
    
obtained_f1 = [
    objective[0]
    for objective in objectives
]

obtained_f2 = [
    objective[1]
    for objective in objectives
]

true_f1 = [
    point[0]
    for point in reference_front
]

true_f2 = [
    point[1]
    for point in reference_front
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

results_dir = os.path.abspath(
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