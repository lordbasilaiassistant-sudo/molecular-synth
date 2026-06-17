# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 78.973 -> 64.32  (19% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 12 nt;
  staples with >14 nt repeat (off-target risk) = 0
- staple cross-dimer screen: worst staple-staple complement = 11 nt
  in 19 flagged pair(s) (>=8 nt); <=~10 nt is benign

## Per-staple melting-temperature histogram (deg C)
mean 59.2  stdev 3.64  range 50.3-68.2
    50.3 | #### 1
    51.4 | #### 1
    52.5 | #### 1
    53.6 | #### 1
    54.8 | ################# 4
    55.9 | ############# 3
    57.0 | ################# 4
    58.1 | ########################## 6
    59.2 | #### 1
    60.4 | ###################### 5
    61.5 | ######################################## 9
    62.6 | ######## 2
    63.7 | ######## 2
    64.8 |  0
    66.0 |  0
    67.1 | #### 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
