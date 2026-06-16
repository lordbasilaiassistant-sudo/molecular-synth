# the-ladder.md — from DNA to a matter compiler, one demonstrated rung at a time

> "If we can figure out DNA, we can figure out this."

As a research thesis, that is **largely correct** — and this file is the honest proof.
DNA is the most programmable matter humanity has, and the field is *already* using it as
the scaffolding to position and direct the synthesis of **other** matter. There is a real
staircase from "fold a nanoshape" toward "program molecular manufacturing." Every rung
below has an actual peer-reviewed lab demonstration. The honesty is in labelling **how
far up each rung is** — proof-of-concept is not the same as general, fast, and scalable.

This is the bridge between the [buildable](science.md) track (our desk) and the
[north-star](north-star.md) (not demonstrated). Call it the **demonstrated frontier**:
real, shown once, not yet a factory.

## The staircase (each rung is demonstrated)

| Rung | What it does | Demonstrated by | Where it is |
|---|---|---|---|
| **0. Program nm shapes** | fold a single ssDNA + staples into an arbitrary ~10–100 nm shape | Rothemund 2006; Douglas 2009 | **on this repo's desk rig** |
| **1. Harden to inorganic** | transcribe the DNA shape into rigid silica / solid metal | Liu 2018 (*Nature*); Sun 2014 (*Science*) | **on this repo (sol–gel)** |
| **2. DNA as a breadboard** | place proteins, enzymes, nanoparticles, catalysts at nm precision; wire enzyme cascades that channel substrates | Fu et al. 2012 (*JACS*, enzyme cascades); Kuzyk et al. 2012 (*Nature*, plasmonic placement) | lab — **and now in our compiler** (`--decorate`: emits orthogonal handle staples + a breadboard map of anti-handles to attach guests) |
| **3. DNA-templated synthesis** | use base-pairing to bring reactants together and **direct/accelerate specific chemical reactions** — programming chemistry with sequence | Gartner & Liu 2001 (*JACS*); Li & Liu 2004 (*Angew. Chem.*) | lab |
| **4. Molecular robots** | DNA walkers/robots that move, sort cargo, and make decisions | Thubagere et al. 2017 (*Science*, a cargo-sorting DNA robot) | lab |
| **5. Artificial assemblers** | a synthetic machine that reads a track and **builds a defined product sequence-specifically** — a primitive assembler | Lewandowski/Leigh 2013 (*Science*, peptide synthesizer); Kassem/Leigh 2017 (*Nature*, stereodivergent synthesis) | lab, ng–mg, slow, bespoke |
| **6+. General molecular manufacturing** | arbitrary products, programmable, parallel, fast, scalable | — | **NOT demonstrated — north-star** |

## The honest read

Rungs **0–5 are each real** — not science fiction, not hand-waving. A synthetic molecular
machine that builds a chosen peptide sequence by reading a molecular "tape" **already
exists** (Leigh, 2013/2017). DNA robots that sort cargo **already exist** (2017).
Programming a chemical reaction with DNA sequence **already works** (Liu, 2001+).

What is **missing** between rung 5 and rung 6 is not magic — it is **generality,
parallelism, scale, and speed**: turning bespoke, nanogram, hours-long proof-of-concepts
into a programmable factory that makes arbitrary products fast. That is a hard,
multi-decade science-and-engineering climb. But it is a **staircase with real steps**,
not a leap of faith — which is exactly why the thesis holds: *we did figure out DNA, and
the same programmability is being extended, rung by rung, to matter beyond DNA.*

## Where this project stands (no inflation)

We live on **rungs 0–1, on a desk** (fold a shape, harden it) and have just **stepped onto
rung 2**: the compiler's `--decorate` emits functional handle staples that position a guest
(enzyme/catalyst/nanoparticle) at a chosen site, with the anti-handle map to attach it — a
glucose-oxidase/HRP cascade on origami is the textbook case (Fu 2012). We point honestly up
the staircase and we do not claim to be standing higher than we are. The
[north-star](north-star.md) stays simulated and labelled. But the direction is real, the
steps above us are published, and the way you climb a staircase is one tested rung at a
time. That is the plan. We climb.

## Citations
- Rothemund, *Nature* 440:297 (2006); Douglas et al., *Nature* 459:414 (2009).
- Liu, X. et al., *Nature* 559:593 (2018); Sun, W. et al., *Science* 346:1258361 (2014).
- Fu, J. et al., *J. Am. Chem. Soc.* 134:5516 (2012); Kuzyk, A. et al., *Nature* 483:311 (2012).
- Gartner, Z.J. & Liu, D.R., *J. Am. Chem. Soc.* 123:6961 (2001); Li, X. & Liu, D.R.,
  *Angew. Chem. Int. Ed.* 43:4848 (2004).
- Thubagere, A.J. et al., *Science* 357:eaan6558 (2017).
- Lewandowski, B. et al., *Science* 339:189 (2013); Kassem, S. et al. (Leigh),
  *Nature* 549:374 (2017).
