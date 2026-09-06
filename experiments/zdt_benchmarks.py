import sys
import os
import math
import statistics
import random
import time
import csv

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)

from spea2 import spea2,zdt1,zdt2,zdt3,zdt4,zdt6
from metrics.igd import calculate_igd
from metrics.gd import calculate_gd
from metrics.hypervolume import calculate_hypervolume
from metrics.spacing import calculate_spacing

POPULATION_SIZE=100
ARCHIVE_SIZE=100
GENERATIONS=250
RUNS=10

problems={
    "ZDT1":(zdt1,30),
    "ZDT2":(zdt2,30),
    "ZDT3":(zdt3,30),
    "ZDT4":(zdt4,30),
    "ZDT6":(zdt6,10)
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

        points_per_interval=num_points//len(intervals)

        for start,end in intervals:
            for i in range(points_per_interval):
                f1=start+(end-start)*i/(points_per_interval-1)
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

def run_problem(problem_name,objective_function,num_variables):
    if problem_name=="ZDT4":
        lower_bound=[0.0]+[-5.0]*(num_variables-1)
        upper_bound=[1.0]+[5.0]*(num_variables-1)
    else:
        lower_bound=0.0
        upper_bound=1.0

    reference_front=generate_reference_front(problem_name)

    raw_results=[]

    for seed in range(1,RUNS+1):
        random.seed(seed)

        start_time=time.perf_counter()

        _,archive=spea2(
            POPULATION_SIZE,
            num_variables,
            ARCHIVE_SIZE,
            GENERATIONS,
            lower_bound,
            upper_bound,
            objective_function
        )

        runtime=time.perf_counter()-start_time

        objectives=[
            objective_function(solution)
            for solution in archive
        ]

        hv=calculate_hypervolume(
            objectives,
            [1.1,1.1]
        )

        igd=calculate_igd(
            objectives,
            reference_front
        )

        gd=calculate_gd(
            objectives,
            reference_front
        )

        spacing=calculate_spacing(
            objectives
        )

        raw_results.append({
            "benchmark":problem_name,
            "seed":seed,
            "hv":hv,
            "igd":igd,
            "gd":gd,
            "spacing":spacing,
            "archive_size":len(archive),
            "nfe":POPULATION_SIZE+GENERATIONS*POPULATION_SIZE,
            "runtime_seconds":runtime
        })

    return raw_results

all_results=[]

for problem_name,(objective_function,num_variables) in problems.items():
    results=run_problem(
        problem_name,
        objective_function,
        num_variables
    )

    all_results.extend(results)

    print()
    print("==========",problem_name,"==========")

    hv=[r["hv"] for r in results]
    igd=[r["igd"] for r in results]
    gd=[r["gd"] for r in results]
    spacing=[r["spacing"] for r in results]

    print(f"HV: {statistics.mean(hv):.6f} ± {statistics.stdev(hv):.6f}")
    print(f"IGD: {statistics.mean(igd):.6f} ± {statistics.stdev(igd):.6f}")
    print(f"GD: {statistics.mean(gd):.6f} ± {statistics.stdev(gd):.6f}")
    print(f"Spacing: {statistics.mean(spacing):.6f} ± {statistics.stdev(spacing):.6f}")

os.makedirs(
    os.path.join(
        os.path.dirname(__file__),
        "../results"
    ),
    exist_ok=True
)

raw_path=os.path.join(
    os.path.dirname(__file__),
    "../results/raw_metrics.csv"
)

with open(raw_path,"w",newline="") as file:
    writer=csv.DictWriter(
        file,
        fieldnames=[
            "benchmark",
            "seed",
            "hv",
            "igd",
            "gd",
            "spacing",
            "archive_size",
            "nfe",
            "runtime_seconds"
        ]
    )

    writer.writeheader()
    writer.writerows(all_results)

summary=[]

for problem_name in problems:
    results=[
        r
        for r in all_results
        if r["benchmark"]==problem_name
    ]

    row={
        "benchmark":problem_name,
        "runs":len(results)
    }

    for metric in [
        "hv",
        "igd",
        "gd",
        "spacing",
        "archive_size",
        "nfe",
        "runtime_seconds"
    ]:
        values=[
            r[metric]
            for r in results
        ]

        row[f"{metric}_mean"]=statistics.mean(values)
        row[f"{metric}_std"]=statistics.stdev(values)
        row[f"{metric}_median"]=statistics.median(values)
        row[f"{metric}_min"]=min(values)
        row[f"{metric}_max"]=max(values)

    summary.append(row)

summary_path=os.path.join(
    os.path.dirname(__file__),
    "../results/summary_metrics.csv"
)

with open(summary_path,"w",newline="") as file:
    writer=csv.DictWriter(
        file,
        fieldnames=summary[0].keys()
    )

    writer.writeheader()
    writer.writerows(summary)