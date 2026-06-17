# Yield diagnostic - square_pyramid

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 53.052 -> 44.529  (16% lower objective)
- staples: 27  (crossover-bridging 15,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 11 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 56.9  stdev 3.03  range 52.1-62.2
    52.1 | ######################################## 4
    52.7 | ########## 1
    53.4 |  0
    54.0 | ############################## 3
    54.6 | ########## 1
    55.3 | #################### 2
    55.9 | ############################## 3
    56.5 | ########## 1
    57.2 | ########## 1
    57.8 | ############################## 3
    58.4 | #################### 2
    59.1 | ########## 1
    59.7 |  0
    60.3 | #################### 2
    61.0 | ########## 1
    61.6 | #################### 2

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ############ 12
  1 crossover(s): ############### 15

## Length distribution
min 32  mean 37.3  max 42 nt (target 32-42)
