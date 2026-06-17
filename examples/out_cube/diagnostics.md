# Yield diagnostic - cube

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 84.531 -> 64.429  (24% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 11 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 58.8  stdev 3.64  range 51.4-67.2
    51.4 | ################ 2
    52.4 | ######## 1
    53.4 | ######## 1
    54.4 | ################################ 4
    55.4 | ######################## 3
    56.4 | ######################################## 5
    57.3 | ######################## 3
    58.3 | ################################ 4
    59.3 | ######################## 3
    60.3 | ######################## 3
    61.3 | ######################## 3
    62.3 | ################################ 4
    63.3 | ######################## 3
    64.3 | ######## 1
    65.2 |  0
    66.2 | ######## 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
