# vision.md — the Synthesizer Thesis (and what's real *today*)

You want the Orville/Star-Trek synthesizer: ask for it — hot coffee, iced coffee, food,
a phone — and it appears. That is the right north star. This file is the honest map of
it, held to the project rule: **we only keep pushing on the parts that are possible in
today's world with today's cheap materials.**

## The honest truth, in one line

A **universal matter replicator** — arbitrary macroscopic, *functional* objects
materialised from atoms on demand — is **not possible today, at any price.** It needs
positional covalent mechanosynthesis (atom-by-atom assembly of bulk solids), which has
**never been demonstrated** (DFT/simulation only — see [`north-star.md`](north-star.md)).
Anyone who tells you otherwise is selling something.

**But the *spirit* of "ask, and a machine makes it" is partly real right now** — not as
one god-box, but as a **federation of cheap desktop makers, each within its domain,
orchestrated by an AI request-compiler** (the same architecture as this repo's
shape→DNA compiler: *request → compiler → machine recipe → physical output*).

## What "ask for X" can actually do — buildable-today matrix

| You ask for… | Real on a cheap desktop **today**? | What actually makes it | Honest limit |
|---|---|---|---|
| **A glass of drinkable water** | ✅ **Yes** | **Water Synth** ([`/synth`](../synth/)) — a Peltier condenses it out of humid air (atmospheric water generation), carbon filter + UV-C → potable | harvested + treated from air, not materialised from energy; "instant" = dispense from a buffer tank |
| **Hot / iced coffee, mixed drinks** | ✅ **Yes** | **Drink Synth** ([`/synth`](../synth/)) — peristaltic pumps + Peltier hot/cold + Arduino | *assembles* from stocked ingredients; does not synthesise coffee from atoms |
| A custom object / phone **case** | ✅ Yes | FDM / resin 3D printer | plastic/resin shape only |
| A meal | 🟡 Partial | food 3D printers / automated cooking | assembles stocked ingredients; not atom-up |
| A **nanostructure**, atomic precision | ✅ Yes (nano only) | **this repo's DNA nanofab** | ~10 nm–1 µm, not macroscopic |
| A **working phone** (chips, battery) | ❌ No (today) | needs semiconductor fabs + multi-material assembly | desktop can't make ICs/cells |
| **Arbitrary macroscopic matter from atoms** (true replicator) | ❌ **North-star** | positional mechanosynthesis (undemonstrated) | [`north-star.md`](north-star.md) |

## The water case — why "a glass of water" is the tractable one

It's worth separating two meanings of "synthesize water," because they have opposite
verdicts:

1. **Materialise H₂O from energy** (a true replicator conjuring water from nothing).
   Bounded by E=mc²: a 250 mL glass is ~0.25 kg ≈ **2.2 × 10¹⁶ J** — a multi-megaton
   energy budget per glass, plus an unsolved way to assemble it. **North-star.**
2. **"A glass of drinkable water appears on demand"** — the lived experience. This is
   **real and cheap today**: **atmospheric water generation** condenses water out of the
   air (a Peltier — the same part as the molecular rig — cooled below the dew point),
   then carbon-filter + UV-C makes it potable. MOF harvesters even pull water from
   <20%-humidity desert air (Kim et al., *Science* 356:430, 2017). "Instant" is just
   dispensing from a buffer tank the harvester keeps filled.

So the intuition "water should be doable" is **correct** — it's the most tractable of
all the examples, and it's genuinely humanity-useful (clean water from air). We built it
([`/synth`](../synth/) `watersynth`). What stays north-star is *materialising* it from
energy, not *having it on demand*.

## The thesis we *can* build toward, honestly

> **The synthesizer = an AI request-compiler that routes "I want X" to the right cheap
> desktop maker, and we add makers one domain at a time — only where today + cheap
> allows.**

Two instances live in this repo, sharing the exact same pattern:

1. **Molecular Synth** (the deep-tech flagship) — *atomic precision*, nanoscale. Shape →
   DNA staple recipe → folded nanostructure → optional silica hardening. This is the
   rung almost nobody has on their desk; it's the hard, novel one.
2. **Drink Synth** ([`/synth`](../synth/)) — *macroscale, today, ~$120 of cheap parts*.
   "iced oat latte" → recipe → pump/heater/chiller command sequence → a drink in a cup.
   It proves the "ask → it makes it" loop is buildable now, and it reuses the same
   repurposed-parts ethos (Peltier, Arduino, peristaltic pumps).

Both are the *same machine philosophy* at different scales: a request gets **compiled**
to a deterministic machine recipe by software, executed by cheap hardware. New domains
(3D-print router, automated kitchen, PCB mill) plug into the same request-compiler as
they become cheap and reliable.

## The rule that keeps this real

Every domain we add must pass the project's gate ([`../validate`](../validate)): the
hardware is **orderable online today and cheap**, and any *capability* we claim is
**demonstrated**. The dream (universal replicator) stays explicitly on the north-star
track, simulated and labelled, until the physics that would unlock it is itself
demonstrated. We build the rungs we can actually stand on — and we keep climbing.
