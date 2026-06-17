# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 170.151 -> 143.464  (16% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 14 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 66.1  stdev 6.59  range 45.0-78.0
    45.0 | #### 1
    47.1 |  0
    49.1 |  0
    51.2 | #### 1
    53.3 |  0
    55.3 |  0
    57.4 | #### 1
    59.5 | ################# 4
    61.5 | ######################################## 9
    63.6 | ############################### 7
    65.7 | #### 1
    67.7 | ######## 2
    69.8 | ###################### 5
    71.8 | ################# 4
    73.9 | ################# 4
    76.0 | ######## 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
