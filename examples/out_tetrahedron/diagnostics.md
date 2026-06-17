# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 50.731 -> 35.979  (29% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 12 nt;
  staples with >14 nt repeat (off-target risk) = 0
- staple cross-dimer screen: worst staple-staple complement = 8 nt
  in 1 flagged pair(s) (>=8 nt); <=~10 nt is benign

## Per-staple melting-temperature histogram (deg C)
mean 60.2  stdev 2.69  range 55.2-68.3
    55.2 | ########## 1
    56.0 |  0
    56.9 | ########## 1
    57.7 | ############################## 3
    58.5 | ############################## 3
    59.3 | ########## 1
    60.1 | ######################################## 4
    61.0 | ############################## 3
    61.8 | #################### 2
    62.6 |  0
    63.4 | ########## 1
    64.2 |  0
    65.1 |  0
    65.9 |  0
    66.7 |  0
    67.5 | ########## 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
