# F1 KDS-EL framework: concise content spec

## Overall style

- Three equal-width panels: `(a)` framework, `(b)` MI-guided init, `(c)` KER flip-score.
- Same light palette (blue / yellow / green / orange / grey) with dark strokes.
- Short labels only; no paragraphs inside the figure.
- Panel `(a)` uses a symmetric vertical main flow with two dashed feedback loops.

## (a) Overall framework

Center flow:

`Raw data X -> MI-guided init -> Two-phase loop -> Dual update -> Eval + W -> KER top-3 -> Compact subset`

Left dashed loop: `Eval + W -> Two-phase loop`, label `t+1`.

Right dashed loop: `Eval + W -> MI-guided init`, label `stall>=20`.

## (b) MI-guided init

Small table (4 features):

| f_j | I(f_j;Y) | theta=.6 | seed |
| --- | -------- | -------- | ---- |
| f7  | .91      | check    | 1    |
| f2  | .78      | check    | 1    |
| f5  | .66      | check    | 1    |
| f9  | .43      | cross    | 0    |

Then symmetric branches `50% MI seed` and `50% rand seed` merge into `N=20 initial pop`.

## (c) KER flip-score

Three elites as binary rows:

`E1 = 1 0 1 1 0`

`E2 = 1 1 0 0 1`

`E3 = 1 0 1 0 1`

Importance row: `W = .8 .2 .7 .5 .9`.

Flip score: `sigma_j = +W_j if x_j = 0`, `sigma_j = -W_j if x_j = 1`.

Two symmetric branches: `90% W-guided` and `10% random`, both `flip phi D`, then `Keep if f improves`.
