# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 78.973 -> 64.321  (19% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 12 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 59.0  stdev 3.58  range 49.9-66.6
    49.9 | ##### 1
    51.0 | ########## 2
    52.0 |  0
    53.1 |  0
    54.1 | ##### 1
    55.1 | ############### 3
    56.2 | ################################### 7
    57.2 | ##### 1
    58.2 | #################### 4
    59.3 | ######################################## 8
    60.3 | ########## 2
    61.4 | #################### 4
    62.4 | ############################## 6
    63.4 |  0
    64.5 | ##### 1
    65.5 | ##### 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
