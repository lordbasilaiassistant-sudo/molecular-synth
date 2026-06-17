# Yield diagnostic - square_pyramid

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 128.917 -> 120.72  (6% lower objective)
- staples: 27  (crossover-bridging 15,
  overloaded >2 crossovers: 0)
- off-target screen: longest scaffold-repeat inside a staple = 14 nt;
  staples with >14 nt repeat (off-target risk) = 0

## Per-staple melting-temperature histogram (deg C)
mean 69.4  stdev 4.99  range 59.6-77.1
    59.6 | ############# 1
    60.7 | ############# 1
    61.8 | ########################## 2
    62.9 | ############# 1
    64.0 | ############# 1
    65.1 | ######################################## 3
    66.2 | ########################## 2
    67.3 |  0
    68.3 | ############# 1
    69.4 | ########################## 2
    70.5 | ########################## 2
    71.6 | ######################################## 3
    72.7 | ############# 1
    73.8 | ########################## 2
    74.9 | ########################## 2
    76.0 | ######################################## 3

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ############ 12
  1 crossover(s): ############### 15

## Length distribution
min 32  mean 37.3  max 42 nt (target 32-42)
