import sys
import os
import math
import statistics

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)

from spea2 import (
    spea2,
    zdt1,
    zdt2,
    zdt3,
    zdt4,
    zdt6
)

from metrics.igd import calculate_igd
from metrics.gd import calculate_gd
from metrics.hypervolume import calculate_hypervolume
from metrics.spacing import calculate_spacing


POPULATION_SIZE = 100
ARCHIVE_SIZE = 100
GENERATIONS = 500
RUNS = 10


problems = {
    "ZDT1": (zdt1, 30),
    "ZDT2": (zdt2, 30),
    "ZDT3": (zdt3, 30),
    "ZDT4": (zdt4, 30),
    "ZDT6": (zdt6, 10)
}


def generate_reference_front(problem_name,num_points=1000):
    reference=[]

    if problem_name=="ZDT1":
        for i in range(num_points+1):
            f1=i/num_points
            f2=1-math.sqrt(f1)
            reference.append([f1,f2])

    elif problem_name=="ZDT2":
        for i in range(num_points+1):
            f1=i/num_points
            f2=1-f1**2
            reference.append([f1,f2])

    elif problem_name=="ZDT3":
        intervals=[
            (0.0,0.0830015349),
            (0.1822287280,0.2577623634),
            (0.4093136748,0.4538821041),
            (0.6183967944,0.6525117038),
            (0.8233317983,0.8518328654)
        ]

        for start,end in intervals:
            for i in range(num_points//len(intervals)):
                f1=start+(end-start)*i/(num_points//len(intervals)-1)
                f2=1-math.sqrt(f1)-f1*math.sin(10*math.pi*f1)
                reference.append([f1,f2])

    elif problem_name=="ZDT4":
        for i in range(num_points+1):
            f1=i/num_points
            f2=1-math.sqrt(f1)
            reference.append([f1,f2])

    elif problem_name=="ZDT6":
        f1_min=0.280775

        for i in range(num_points+1):
            f1=f1_min+(1-f1_min)*i/num_points
            f2=1-f1**2
            reference.append([f1,f2])

    return reference


def run_problem(
    problem_name,
    objective_function,
    num_variables
):
    if problem_name == "ZDT4":
        lower_bound = [0.0] + [-5.0] * (num_variables - 1)
        upper_bound = [1.0] + [5.0] * (num_variables - 1)
    else:
        lower_bound = 0.0
        upper_bound = 1.0

    reference_front = generate_reference_front(
        problem_name
    )

    igd_values = []
    gd_values = []
    hv_values = []
    spacing_values = []

    for run in range(RUNS):
        _, archive = spea2(
            POPULATION_SIZE,
            num_variables,
            ARCHIVE_SIZE,
            GENERATIONS,
            lower_bound,
            upper_bound,
            objective_function
        )

        objectives = [
            objective_function(solution)
            for solution in archive
        ]

        igd_values.append(
            calculate_igd(
                objectives,
                reference_front
            )
        )

        gd_values.append(
            calculate_gd(
                objectives,
                reference_front
            )
        )

        hv_values.append(
            calculate_hypervolume(
                objectives,
                [1.1, 1.1]
            )
        )

        spacing_values.append(
            calculate_spacing(
                objectives
            )
        )

    return {
        "IGD": (
            statistics.mean(igd_values),
            statistics.stdev(igd_values)
        ),
        "GD": (
            statistics.mean(gd_values),
            statistics.stdev(gd_values)
        ),
        "Hypervolume": (
            statistics.mean(hv_values),
            statistics.stdev(hv_values)
        ),
        "Spacing": (
            statistics.mean(spacing_values),
            statistics.stdev(spacing_values)
        )
    }


for problem_name, (
    objective_function,
    num_variables
) in problems.items():

    results = run_problem(
        problem_name,
        objective_function,
        num_variables
    )

    print()
    print(
        "==========",
        problem_name,
        "=========="
    )

    for metric, (mean, std) in results.items():
        print(
            f"{metric}: "
            f"{mean:.6f} ± {std:.6f}"
        )