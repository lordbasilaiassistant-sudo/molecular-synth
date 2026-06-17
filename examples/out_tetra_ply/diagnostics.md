# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 53.428 -> 39.517  (26% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 11 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 57.1  stdev 3.23  range 51.7-63.9
    51.7 | ######## 1
    52.5 |  0
    53.2 | ################################ 4
    54.0 | ######## 1
    54.8 | ######## 1
    55.5 |  0
    56.3 | ######################################## 5
    57.1 | ################ 2
    57.8 |  0
    58.6 | ######## 1
    59.4 | ######## 1
    60.1 | ######## 1
    60.9 | ######## 1
    61.6 |  0
    62.4 | ######## 1
    63.2 | ######## 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 41 nt (target 32-42)
