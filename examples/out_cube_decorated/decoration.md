# Decoration map (DNA breadboard) - cube


Rung 2 of the ladder: each handle below protrudes from the folded origami at a known
site. Attach your guest (enzyme / catalyst / nanoparticle / dye) by conjugating it to the
**anti-handle** (the reverse complement); it then hybridises to the handle and is
positioned at that site. Order the decorated staples as their full `order_sequence`
(staple + TT spacer + handle, on the 3p end) - see
staples.csv.

| Site | Guest | Staple (well) | Location | End | Handle (on origami, 5'->3') | Anti-handle (on guest, 5'->3') |
|------|-------|---------------|----------|-----|------------------------------|--------------------------------|
| A | glucose-oxidase | cube-st039 (H5) | edge (4, 6) | 3p | `ATTTGCTGCTTAGTGGACGC` | `GCGTCCACTAAGCAGCAAAT` |
| B | HRP | cube-st027 (D4) | edge (5, 7) | 3p | `GAGGATCTATGGCAGCCGTA` | `TACGGCTGCCATAGATCCTC` |
| C | fluorophore | cube-st013 (F2) | edge (0, 2) | 3p | `TGCGAGGTAACCTTTCGATC` | `GATCGAAAGGTTACCTCGCA` |

**How to attach a guest:**
1. Conjugate the **anti-handle** oligo to your guest (NHS-ester/thiol/click for proteins;
   thiol-DNA for Au nanoparticles; or buy the guest pre-modified).
2. After folding + purifying the origami, add the guest-anti-handle in modest excess.
3. Incubate (RT, in the Mg2+ buffer); it hybridises to its handle at the mapped site.
4. Verify placement by gel shift / AFM / TEM (handles add mass at known positions).

> Honest scope: handles POSITION a guest you supply; they do not synthesise it. This is
> demonstrated origami functionalisation (Fu et al. 2012; Kuzyk et al. 2012) - the first
> chemistry-capable rung of docs/the-ladder.md.
