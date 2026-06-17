# Yield diagnostic - square

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 75.302 -> 58.819  (22% lower objective)
- staples: 14  (crossover-bridging 7,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 14 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 68.2  stdev 3.66  range 62.1-74.4
    62.1 | ######################################## 3
    62.9 |  0
    63.6 |  0
    64.4 |  0
    65.2 |  0
    65.9 | ############# 1
    66.7 |  0
    67.5 | ######################################## 3
    68.2 | ############# 1
    69.0 | ############# 1
    69.8 | ############# 1
    70.5 | ############# 1
    71.3 | ########################## 2
    72.1 |  0
    72.8 |  0
    73.6 | ############# 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ####### 7
  1 crossover(s): ####### 7

## Length distribution
min 32  mean 36.0  max 41 nt (target 32-42)
