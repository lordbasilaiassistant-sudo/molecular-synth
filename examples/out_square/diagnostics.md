# Yield diagnostic - square

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 74.702 -> 58.254  (22% lower objective)
- staples: 14  (crossover-bridging 7,
  overloaded >2 crossovers: 0)

## Per-staple melting-temperature histogram (deg C)
mean 68.2  stdev 3.82  range 62.1-74.5
    62.1 | ######################################## 3
    62.9 |  0
    63.7 |  0
    64.5 |  0
    65.2 |  0
    66.0 | ############# 1
    66.8 | ########################## 2
    67.5 | ############# 1
    68.3 | ############# 1
    69.1 | ########################## 2
    69.9 |  0
    70.6 |  0
    71.4 | ########################## 2
    72.2 | ############# 1
    73.0 |  0
    73.7 | ############# 1

-> tight Tm distribution -> cooperative anneal expected (good)

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ####### 7
  1 crossover(s): ####### 7

## Length distribution
min 32  mean 36.0  max 41 nt (target 32-42)
