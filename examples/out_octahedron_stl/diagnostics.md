# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 84.531 -> 71.064  (16% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 11 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 58.8  stdev 4.16  range 48.9-69.9
    48.9 | ##### 1
    50.2 |  0
    51.5 | ##### 1
    52.8 | ################# 3
    54.1 | ########### 2
    55.4 | ######################################## 7
    56.7 | ############################ 5
    58.1 | ################# 3
    59.4 | ###################### 4
    60.7 | ######################################## 7
    62.0 | ##### 1
    63.3 | ############################ 5
    64.6 | ##### 1
    65.9 |  0
    67.3 |  0
    68.6 | ##### 1

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
