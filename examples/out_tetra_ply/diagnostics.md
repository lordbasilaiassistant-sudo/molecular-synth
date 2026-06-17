# Yield diagnostic - tetrahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 50.731 -> 37.798  (25% lower objective)
- staples: 20  (crossover-bridging 11,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 12 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 60.1  stdev 3.12  range 55.5-66.5
    55.5 | ######################################## 3
    56.2 | ############# 1
    56.9 | ############# 1
    57.6 | ########################## 2
    58.2 | ############# 1
    58.9 |  0
    59.6 | ######################################## 3
    60.3 | ############# 1
    61.0 | ########################## 2
    61.7 | ############# 1
    62.4 | ############# 1
    63.1 | ########################## 2
    63.7 |  0
    64.4 | ############# 1
    65.1 |  0
    65.8 | ############# 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ######### 9
  1 crossover(s): ########### 11

## Length distribution
min 32  mean 37.8  max 42 nt (target 32-42)
