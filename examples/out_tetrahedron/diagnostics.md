# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 100.218 -> 79.441  (21% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 14 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 68.4  stdev 4.4  range 62.2-80.5
    62.2 | ################################ 4
    63.4 |  0
    64.5 | ######## 1
    65.7 | ######## 1
    66.8 | ######################################## 5
    67.9 | ######## 1
    69.1 | ################ 2
    70.2 | ######################## 3
    71.3 |  0
    72.5 |  0
    73.6 | ################ 2
    74.8 |  0
    75.9 |  0
    77.0 |  0
    78.2 |  0
    79.3 | ######## 1

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
