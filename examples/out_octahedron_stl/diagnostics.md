# Yield diagnostic - octahedron

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: 169.551 -> 152.218  (10% lower objective)
- staples: 41  (crossover-bridging 23,
  overloaded >2 crossovers: 0)

## Per-staple melting-temperature histogram (deg C)
mean 66.2  stdev 6.05  range 49.8-78.3
    49.8 | #### 1
    51.6 |  0
    53.4 | #### 1
    55.2 |  0
    57.0 | ######## 2
    58.7 | ######## 2
    60.5 | ################ 4
    62.3 | #################### 5
    64.1 | #################### 5
    65.9 | ################ 4
    67.7 |  0
    69.4 | ######################################## 10
    71.2 | ############ 3
    73.0 | #### 1
    74.8 | #### 1
    76.6 | ######## 2

-> broad Tm distribution -> screen Mg2+/ramp; some staples are outliers

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
  0 crossover(s): ################## 18
  1 crossover(s): ####################### 23

## Length distribution
min 32  mean 36.9  max 42 nt (target 32-42)
