# /catalog — the Maker Catalog

An **ever-extending, queryable library of what one synthesizer-system can make.** Ask
"can we make X?" and it decomposes X into its real substance, gives an honest feasibility
verdict, and routes it to a maker. Some items have **two styles in one system** (water:
harvest-from-air vs. from-reservoir). The point: *a cookie isn't "a cookie" — it's
ingredients → molecules → atoms (→ DNA where biological)*, and every target gets that
treatment plus a **check**.

```bash
cd catalog
python -m makerlib check "glass of cold water"
python -m makerlib check "cookie"
python -m makerlib list --feasibility ready
```

## The rule: the catalog is the *menu of what the synth can make*

**If the synth can't make it, it isn't a catalog item.** A working phone and "matter from
energy" aren't synth-makeable, so they are **not** in [`items.json`](items.json). The
`check`/`order` brain still *recognises* such requests and **honestly declines** them
(verdict `north-star`, routed to [`../docs/north-star.md`](../docs/north-star.md)) — but
the menu only lists things this class of machine can actually make.

## The feasibility ladder

| Verdict | In the catalog? | Meaning |
|---|---|---|
| **ready** | ✅ yes | a maker in this repo makes it today (`watersynth` / `drinksynth` / `molsynth`) |
| **assemble** | ✅ yes | a cheap real-world maker (kitchen, 3D printer) makes it; integration planned |
| **frontier** | ✅ yes | synth-makeable in principle, demonstrated in a lab; on the [ladder](../docs/the-ladder.md) |
| **north-star** | ❌ no | not synth-makeable — recognised + declined, lives in [north-star.md](../docs/north-star.md) |

## Order brain (voice / AI front door)

```bash
python -m makerlib order "whiskey on the rocks"   # -> ICE (watersynth) + POUR whiskey (drinksynth)
python -m makerlib order "g&t"                     # gin + tonic + ice + lime
python -m makerlib order "cookie"                  # falls through to the catalog (assemble)
```
It resolves cocktail slang + modifiers (on the rocks / neat / up / double / dirty) and
composes a **cross-maker** plan. Rule-based by default; pass an **LLM hook**
(`order(text, llm=callable)`) for a real-AI parse of arbitrary phrasing — the Orville
"just ask" experience. **Voice** is an input adapter: a speech-to-text front end (browser
Web Speech API, or a local whisper model) feeds the recognised text into `order`.

> **The catalog is an engine of the one front door.** `synth/itemsynth` is the federation's
> single entry point; its `feasibility()` and `plan()` delegate to this package's `check` and
> `order`, and `synthesize()` falls back here for cross-maker / cataloged asks. So you can
> reach the catalog directly (`python -m makerlib ...`) *or* through `itemsynth` — one spine,
> two doors into it.

Each item lists its **decomposition** (the substance ladder), its **styles** (method +
maker + feasibility + what it needs + a citation), and honest **notes**. `check` on an
uncataloged thing classifies it by its nearest category and flags it as an estimate to
verify and add.

## Extend it (the cookie principle)

Add an item to [`items.json`](items.json):
1. **Decompose it** — item → components → molecules → atoms (→ DNA/proteins if biological).
2. **Pick the style(s)** — how would the system actually make it, via which maker?
3. **Check feasibility** honestly — ready / assemble / frontier / north-star, with a
   citation where a capability is claimed (same discipline as the [validate gate](../validate)).
4. Run `python -m makerlib check "<your item>"`.

This is the blueprint growing: every checked item is one more thing the one machine can
(or honestly cannot yet) make. The library is the map; the makers ([`../synth`](../synth),
[`../compiler`](../compiler)) are the territory.
