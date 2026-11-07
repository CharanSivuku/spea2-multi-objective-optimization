from src.benchmarks.dtlz import *

# DTLZ1: sum of objectives = 0.5
x = [0.5] * 12
f = dtlz1(x)
print("DTLZ1:", sum(f))

# DTLZ2: sum of squared objectives = 1
f = dtlz2(x)
print("DTLZ2:", sum(v*v for v in f))

# DTLZ3: same global optimum condition
f = dtlz3(x)
print("DTLZ3:", sum(v*v for v in f))

# DTLZ5: degenerate front
f = dtlz5(x)
print("DTLZ5:", f)

# DTLZ6: global PF when all distance variables are zero
x6 = [0.5, 0.5] + [0.0] * 10
f = dtlz6(x6)
print("DTLZ6:", f)

# DTLZ7: g = 1 when all distance variables are zero
x7 = [0.0, 0.0] + [0.0] * 10
f = dtlz7(x7)
print("DTLZ7:", f)