# Yield diagnostic - square

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 32.95 -> 27.574  (16% lower objective)
- staples: 14  (crossover-bridging 7,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 11 nt;
  staples with >14 nt repeat (off-target risk) = 0
- staple cross-dimer screen: worst staple-staple complement = 9 nt
  in 1 flagged pair(s) (>=8 nt); <=~10 nt is benign

## Per-staple melting-temperature histogram (deg C)
mean 60.2  stdev 3.31  range 52.2-65.5
    52.2 | #################### 1
    53.0 |  0
    53.8 |  0
    54.7 |  0
    55.5 |  0
    56.3 | #################### 1
    57.2 | #################### 1
    58.0 | ######################################## 2
    58.8 | ######################################## 2
    59.7 |  0
    60.5 | ######################################## 2
    61.3 |  0
    62.1 | #################### 1
    63.0 | ######################################## 2
    63.8 | #################### 1
    64.6 | #################### 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ####### 7
  1 crossover(s): ####### 7

## Length distribution
min 32  mean 36.0  max 41 nt (target 32-42)
