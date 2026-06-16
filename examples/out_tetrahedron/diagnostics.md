# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 99.018 -> 79.175  (20% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)

## Per-staple melting-temperature histogram (deg C)
mean 68.5  stdev 4.02  range 62.1-76.1
    62.1 | ######################################## 3
    63.0 |  0
    63.9 | ########################## 2
    64.7 |  0
    65.6 | ############# 1
    66.5 | ########################## 2
    67.4 | ######################################## 3
    68.2 |  0
    69.1 |  0
    70.0 | ######################################## 3
    70.8 | ########################## 2
    71.7 | ########################## 2
    72.6 |  0
    73.5 |  0
    74.3 |  0
    75.2 | ########################## 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
