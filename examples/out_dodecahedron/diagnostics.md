# Yield diagnostic - dodecahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 301.515 -> 250.224  (17% lower objective)
- staples: 102  (crossover-bridging 59,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 32 nt;
  staples with >14 nt repeat (off-target risk) = 4
- staple cross-dimer screen: worst staple-staple complement = 11 nt
  in 83 flagged pair(s) (>=8 nt); <=~10 nt is benign

## Per-staple melting-temperature histogram (deg C)
mean 61.8  stdev 5.68  range 51.2-77.5
    51.2 | ######### 4
    52.8 | ############## 6
    54.5 | ################ 7
    56.1 | ######################### 11
    57.8 | ############## 6
    59.4 | ##################### 9
    61.0 | ######################################## 17
    62.7 | ##################################### 16
    64.3 | ################ 7
    66.0 | ################## 8
    67.6 | ## 1
    69.3 | ####### 3
    70.9 |  0
    72.6 | #### 2
    74.2 | ####### 3
    75.9 | #### 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ########################################### 43
  1 crossover(s): ########################################################### 59

## Length distribution
min 32  mean 37.1  max 42 nt (target 32-42)
