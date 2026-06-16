# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 99.018 -> 81.285  (18% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)

## Per-staple melting-temperature histogram (deg C)
mean 68.5  stdev 4.48  range 62.7-77.8
    62.7 | ############# 1
    63.6 | ######################################## 3
    64.6 | ######################################## 3
    65.5 | ########################## 2
    66.5 | ########################## 2
    67.4 | ############# 1
    68.4 | ############# 1
    69.3 |  0
    70.2 | ############# 1
    71.2 | ######################################## 3
    72.1 |  0
    73.1 |  0
    74.0 |  0
    75.0 |  0
    75.9 | ############# 1
    76.9 | ########################## 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
