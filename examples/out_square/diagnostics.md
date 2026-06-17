# Yield diagnostic - square

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 35.875 -> 22.112  (38% lower objective)
- staples: 14  (crossover-bridging 7,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 12 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 60.2  stdev 1.83  range 57.3-63.6
    57.3 | #################### 1
    57.7 | ######################################## 2
    58.1 | #################### 1
    58.5 |  0
    58.9 |  0
    59.3 |  0
    59.7 | ######################################## 2
    60.1 | #################### 1
    60.4 | ######################################## 2
    60.8 | ######################################## 2
    61.2 | #################### 1
    61.6 |  0
    62.0 |  0
    62.4 |  0
    62.8 |  0
    63.2 | ######################################## 2

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ####### 7
  1 crossover(s): ####### 7

## Length distribution
min 32  mean 36.0  max 40 nt (target 32-42)
