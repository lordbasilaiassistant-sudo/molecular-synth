# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 169.551 -> 142.73  (16% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)

## Per-staple melting-temperature histogram (deg C)
mean 66.2  stdev 6.05  range 50.2-77.1
    50.2 | ######## 1
    51.9 | ######## 1
    53.6 |  0
    55.3 | ######## 1
    56.9 |  0
    58.6 | ######################## 3
    60.3 | ######################## 3
    62.0 | ######################################## 5
    63.7 | ######################################## 5
    65.3 | ######################################## 5
    67.0 | ######################## 3
    68.7 | ######################## 3
    70.4 | ################ 2
    72.0 | ######################################## 5
    73.7 | ######## 1
    75.4 | ######################## 3

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
