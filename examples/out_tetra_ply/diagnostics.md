# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 100.218 -> 81.322  (19% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 14 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 68.5  stdev 4.6  range 59.0-76.2
    59.0 | #################### 1
    60.0 |  0
    61.1 |  0
    62.2 | #################### 1
    63.3 | ######################################## 2
    64.3 | ######################################## 2
    65.4 | ######################################## 2
    66.5 | ######################################## 2
    67.6 | #################### 1
    68.7 | #################### 1
    69.7 | #################### 1
    70.8 | ######################################## 2
    71.9 | #################### 1
    73.0 |  0
    74.0 | ######################################## 2
    75.1 | ######################################## 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
