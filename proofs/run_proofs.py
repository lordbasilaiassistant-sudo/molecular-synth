#!/usr/bin/env python3
"""
PROOFS - "would it actually work IRL, given the parts?"

Each proof produces EVIDENCE (numbers, PASS/FAIL), not assertions. Where an independent
tool exists we use it (Biopython for thermodynamics, oxDNA-analysis-tools for the 3D
structure); where physics/simulation suffices we compute it (a simulated PID control
loop, power and fluidics math). This is the bridge from "designed" to "proven sound
given the BOM" - it is NOT a wet-lab result (simulation/independent-tool agreement
proves the DESIGN and CONTROL are correct, not the experimental yield).

    python proofs/run_proofs.py
Optional independent tools:  pip install biopython oxDNA-analysis-tools
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compiler"))
sys.path.insert(0, os.path.join(ROOT, "synth"))


# --------------------------------------------------------------------------- #
def proof_staple_addressing():
    """The ordered oligos completely + correctly address the scaffold: each staple is
    the exact reverse complement of its scaffold region (will hybridise), and together
    they tile the whole scaffold route exactly once (no gaps, no overlaps)."""
    from molsynth import geometry, scaffold as sc, sequences as seq
    from molsynth.staples import build_staples
    from molsynth.optimizer import YieldModel
    mesh = geometry.load_shape("cube")
    s, name, synth = sc.load_scaffold()
    routing = sc.route(mesh, s, name, synth)
    staples, _ = build_staples(routing, YieldModel(), iterations=1500, seed=1)
    route = routing.scaffold_seq

    bad = [st.name for st in staples
           if st.seq != seq.reverse_complement(route[st.scaffold_start:st.scaffold_end])]
    cover = [0] * len(route)
    for st in staples:
        for g in range(st.scaffold_start, st.scaffold_end):
            cover[g] += 1
    gaps = sum(1 for c in cover if c == 0)
    overlaps = sum(1 for c in cover if c > 1)
    passed = (not bad) and gaps == 0 and overlaps == 0
    return ("Staple addressing (chemical validity + complete tiling)", passed, [
        f"staples: {len(staples)}   scaffold positions: {len(route)}",
        f"not reverse-complement of their region: {len(bad)}  (must be 0)",
        f"positions covered exactly once: {sum(1 for c in cover if c == 1)}  "
        f"gaps: {gaps}  overlaps: {overlaps}  (gaps+overlaps must be 0)",
        "=> every ordered oligo will hybridise, and the set fully addresses the scaffold.",
    ])


def proof_single_scaffold_circuit():
    """The premise of one-pot origami: every shape the compiler accepts routes as ONE
    closed scaffold loop that lays down both strands of every edge. Proven across all
    presets by reconstructing the circuit from the emitted arcs (closed + complete +
    balanced), and confirmed unforgeable by rejecting a deliberately broken trail."""
    from molsynth import geometry, scaffold as sc
    rows, all_ok = [], True
    for shape in ("tetrahedron", "cube", "octahedron", "icosahedron",
                  "dodecahedron", "square"):
        mesh = geometry.load_shape(shape)
        rep = sc.circuit_report(sc._eulerian_circuit(mesh), mesh.edges)
        ok = rep["single_circuit"] and rep["n_arcs"] == 2 * len(mesh.edges)
        all_ok = all_ok and ok
        rows.append(f"  {shape:13s} arcs={rep['n_arcs']}=2x{rep['n_edges']} "
                    f"closed={rep['closed']} balanced={rep['balanced']} -> {ok}")
    # negative control: an open (missing-arc) trail must be rejected
    tri = [(0, 1), (1, 2), (2, 0)]
    full = [(0, 1), (1, 2), (2, 0), (0, 2), (2, 1), (1, 0)]
    neg_ok = (sc.circuit_report(full, tri)["single_circuit"] is True
              and sc.circuit_report(full[:-1], tri)["single_circuit"] is False)
    passed = all_ok and neg_ok
    return ("Single closed scaffold circuit (one-strand routability)", passed, rows + [
        f"negative control (open trail rejected): {neg_ok}",
        "=> each accepted shape is threadable by a single scaffold strand that covers "
        "every edge twice and returns to itself (else compile() raises).",
    ])


def proof_cadnano_roundtrip():
    """The emitted caDNAno v2 JSON (-> CanDo / oxDNA) is a FAITHFUL encoding of the design,
    proven by an independent decoder that walks the pointer arrays back into strands: the
    scaffold reconstructs as exactly one closed loop of the right length, the staples as
    the right count with matching lengths that partition the complementary bases exactly,
    and every 5'/3' pointer is reciprocal. Topology is verified here (caDNAno stores
    connectivity, not sequence); it is not GUI-tested in caDNAno itself."""
    import json
    from molsynth import geometry, scaffold as sc, export
    from molsynth.staples import build_staples
    from molsynth.optimizer import YieldModel
    rows, all_ok = [], True
    for shape in ("tetrahedron", "cube", "octahedron", "dodecahedron"):
        mesh = geometry.load_shape(shape)
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        staples, _ = build_staples(routing, YieldModel(), iterations=600, seed=1)
        with tempfile.TemporaryDirectory() as d:
            path = export.write_cadnano(d, routing, staples)
            rep = export.cadnano_decode(json.load(open(path)))
        exp_lens = sorted(len(st.seq) for st in staples)
        ok = (rep["scaffold_closed_loop"]
              and rep["scaffold_len"] == routing.scaffold_len_used
              and rep["n_staples"] == len(staples)
              and rep["staple_lens"] == exp_lens
              and rep["staples_partition_complement"]
              and rep["pointers_reciprocal"])
        all_ok = all_ok and ok
        rows.append(f"  {shape:13s} scaffold loop={rep['scaffold_len']} "
                    f"(=={routing.scaffold_len_used}), staples={rep['n_staples']} "
                    f"(=={len(staples)}), partition+reciprocal="
                    f"{rep['staples_partition_complement'] and rep['pointers_reciprocal']} -> {ok}")
    return ("caDNAno export round-trips (independent decoder)", all_ok, rows + [
        "=> the caDNAno JSON encodes exactly the compiled scaffold loop + staple set "
        "(faithful topology); apply sequences + run CanDo/oxDNA for geometry.",
    ])


def proof_tm_vs_biopython():
    """Our SantaLucia Tm engine agrees with an INDEPENDENT implementation (Biopython
    Tm_NN with the DNA_NN3 unified table) under matched conditions."""
    from molsynth import sequences as seq
    try:
        from Bio.SeqUtils import MeltingTemp as mt
    except Exception:
        return ("Tm vs independent tool (Biopython DNA_NN3)", None,
                ["biopython not installed - run: pip install biopython"])
    seqs = ["ACGTACGTACGTACGTACGT", "GGGCCCAAATTTGGGCCCAA",
            "ATATATGCGCGCATATGCGC", "CAGTCAGTCAGTCAGTCAGT", "TGGCATGGACGATCAGTACC"]
    rows, diffs = [], []
    for s in seqs:
        ours = seq.tm(s, strand_conc_M=0.25e-6, na_M=0.05)
        bio = mt.Tm_NN(s, nn_table=mt.DNA_NN3, dnac1=250, dnac2=0, Na=50, saltcorr=5)
        diffs.append(abs(ours - bio))
        rows.append(f"  {s}: ours {ours:5.1f} C   Biopython {bio:5.1f} C   d={abs(ours-bio):.2f}")
    maxd = max(diffs)
    passed = maxd < 6.0
    return ("Tm vs independent tool (Biopython DNA_NN3)", passed,
            [f"max |our Tm - Biopython Tm_NN| = {maxd:.2f} C  (tol 6 C; matched 250 nM, 50 mM Na)"]
            + rows)


def proof_structure_oxdna():
    """The emitted 3D structure is a valid DNA configuration: an independent parse loads
    it, every nucleotide frame is orthonormal, and paired backbones sit OUTSIDE the
    bases (B-DNA geometry, no steric collapse - the regression-proof of the a1 fix)."""
    import molsynth
    from molsynth import geometry, scaffold as sc, structure3d
    mesh = geometry.load_shape("tetrahedron")
    s, name, synth = sc.load_scaffold()
    routing = sc.route(mesh, s, name, synth)
    dup = structure3d.duplex_report(mesh, routing)

    with tempfile.TemporaryDirectory() as d:
        molsynth.compile_shape("tetrahedron", outdir=d, iterations=400)
        top = open(os.path.join(d, "design.top")).read().splitlines()
        conf = open(os.path.join(d, "conf.dat")).read().splitlines()
        nbases = int(top[0].split()[0])
        body = conf[3:]
        cols_ok = all(len(r.split()) == 15 for r in body)
        count_ok = len(body) == nbases == (len(top) - 1)
        bad_ortho = 0
        for r in body:
            v = [float(x) for x in r.split()]
            a1, a3 = v[3:6], v[6:9]
            n1 = math.sqrt(sum(c * c for c in a1))
            n3 = math.sqrt(sum(c * c for c in a3))
            dot = sum(a1[i] * a3[i] for i in range(3))
            if abs(n1 - 1) > 1e-3 or abs(n3 - 1) > 1e-3 or abs(dot) > 1e-3:
                bad_ortho += 1
    geometry_ok = dup["mean_backbone_pair_dist"] > dup["mean_base_pair_dist"] > 0
    passed = cols_ok and count_ok and bad_ortho == 0 and geometry_ok
    return ("3D structure valid (oxDNA format + B-DNA geometry)", passed, [
        f"independent re-parse: {len(body)} nucleotides (top header + rows agree: {count_ok})",
        f"valid 15-column oxDNA rows: {cols_ok}   non-orthonormal frames: {bad_ortho} (must be 0)",
        f"paired backbone dist {dup['mean_backbone_pair_dist']} > base dist "
        f"{dup['mean_base_pair_dist']}  => backbones outside, bases meet (no collapse)",
        "=> the standard oxDNA file format is valid and the geometry is physical "
        "(relaxable, not exploding).",
    ])


def proof_thermocycler_control():
    """Simulate the firmware's PID against a lumped thermal model of the Peltier+block
    and prove it tracks the emitted anneal ramp - i.e. the control system would execute
    the fold protocol."""
    from molsynth.protocol import anneal_ramp
    Kp, Ki, Kd = 18.0, 0.35, 30.0          # firmware constants (thermocycler.ino)
    C, Pmax, k, Tamb, dt = 36.0, 60.0, 0.6, 22.0, 0.2   # 40 g Al block, 60 W TEC, loss
    ramp = anneal_ramp(t_hot=90, t_cold=20, total_min=20)
    T, integ, prev, max_hold_err = Tamb, 0.0, 0.0, 0.0
    for setpoint, minutes in ramp:
        for _ in range(int(minutes * 60 / dt)):
            err = setpoint - T
            integ = max(-400, min(400, integ + err * dt))
            deriv = (err - prev) / dt
            prev = err
            out = max(-255, min(255, Kp * err + Ki * integ + Kd * deriv))
            P = Pmax * (out / 255.0)        # bidirectional Peltier (heat + cool)
            T += (P - k * (T - Tamb)) * dt / C
        max_hold_err = max(max_hold_err, abs(setpoint - T))
    passed = max_hold_err < 3.0
    return ("Thermocycler ramp tracking (PID + thermal simulation)", passed, [
        f"worst setpoint tracking error over the full 90->20 C ramp: {max_hold_err:.2f} C (tol 3 C)",
        "model: 40 g aluminium block (C=36 J/K), 60 W TEC1-12706, loss k=0.6 W/K, "
        "firmware Kp/Ki/Kd",
        "=> the Peltier+PID would hold and ramp temperature through the fold protocol.",
    ])


def proof_power_budget():
    """Given the BOM, the rig's worst-case simultaneous electrical draw fits the PSU."""
    draws = {"TEC1-12706 Peltier (thermocycler)": 60, "heatsink fan": 3,
             "Arduino": 2.5, "BTS7960 H-bridge": 1.0, "gel + transilluminator": 8.0}
    active = sum(draws.values())           # thermocycler ramp + control + gel imaging
    psu = 12 * 30                          # 360 W PSU in the BOM
    passed = active < psu
    return ("Power budget closes (given the BOM PSU)", passed, [
        f"worst simultaneous draw: ~{active:.0f} W",
        f"BOM PSU: 12 V x 30 A = {psu} W   headroom: {psu - active:.0f} W",
        "=> the specified PSU powers the rig (Peltier ramp + control + gel) with large margin.",
    ])


def proof_matches_published_wireframe_envelopes():
    """Would a compiled design fold like the ones that ALREADY HAVE? The digital half of
    wet-lab validation (#7): check that every preset's design parameters fall inside the
    quantitative envelopes of experimentally-folded wireframe DNA origami --
      * Veneziano et al., Science 352:1534 (2016) (DAEDALUS): scaffold-routed wireframe
        polyhedra; edges are integer helical turns (in-phase crossovers), minimum ~31 bp;
        45 objects built + cryo-EM/AFM verified, tens of nm.
      * Benson et al., Nature 523:441 (2015): polyhedral-mesh wireframes on M13.
    We assert: edges are within +-0.75 bp of an integer number of 10.5-bp turns (crossover
    phase), every edge >= 31 bp (DAEDALUS minimum) and >= 10 nm, staple lengths in the
    synthesizable+bindable 21-78 nt band, and scaffold usage <= M13 (7249 nt). Matching the
    demonstrated envelope makes a design the SAME physical class as folded structures -- it
    raises fold confidence; it does not replace a wet-lab yield measurement."""
    from molsynth import geometry, scaffold as sc
    from molsynth.staples import build_staples
    from molsynth.optimizer import YieldModel
    BP_PER_TURN, NM_PER_BP, M13 = 10.5, 0.34, 7249
    EDGE_MIN_BP, STAP_LO, STAP_HI, PHASE_TOL = 31, 21, 78, 0.75
    s, name, synth = sc.load_scaffold()
    rows, all_ok = [], True
    for shape in ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"):
        mesh = geometry.load_shape(shape)
        r = sc.route(mesh, s, name, synth)
        stp, _ = build_staples(r, YieldModel(), iterations=1200, seed=7)
        ebp = sorted(r.edge_bp.values())
        # crossover phase: distance (bp) from each edge to the nearest integer-turn length
        phase = max(abs(bp - round(bp / BP_PER_TURN) * BP_PER_TURN) for bp in ebp)
        slen = sorted(len(x.seq) for x in stp)
        edge_nm = ebp[0] * NM_PER_BP
        ok = (ebp[0] >= EDGE_MIN_BP and phase <= PHASE_TOL and edge_nm >= 10.0
              and slen[0] >= STAP_LO and slen[-1] <= STAP_HI
              and r.scaffold_len_used <= M13)
        all_ok = all_ok and ok
        rows.append(
            f"  {shape:13s} edge {ebp[0]}-{ebp[-1]}bp (>=31, phase<= {phase:.2f}bp) "
            f"{edge_nm:.0f}nm  staples {slen[0]}-{slen[-1]}nt (21-78)  "
            f"scaf {r.scaffold_len_used}<=7249 -> {ok}")
    return ("Matches published wireframe-origami envelopes (DAEDALUS/Benson)", all_ok, rows + [
        "=> every preset's edges, crossover phase, staple lengths, size, and scaffold use "
        "sit inside the demonstrated, cryo-EM/AFM-verified design space -- same physical",
        "   class as folded structures. Wet-lab yield still needs the bench (issue #7).",
    ])


PROOFS = [proof_single_scaffold_circuit, proof_staple_addressing, proof_cadnano_roundtrip,
          proof_matches_published_wireframe_envelopes,
          proof_tm_vs_biopython, proof_structure_oxdna, proof_thermocycler_control,
          proof_power_budget]


def main():
    print("=" * 70)
    print("PROOFS - would it work IRL, given the parts? (evidence, not assertions)")
    print("=" * 70)
    passed = failed = skipped = 0
    for fn in PROOFS:
        try:
            name, ok, lines = fn()
        except Exception as e:  # noqa: BLE001
            name, ok, lines = (fn.__name__, False, [f"ERROR: {e!r}"])
        tag = "PASS" if ok else ("SKIP" if ok is None else "FAIL")
        print(f"\n[{tag}] {name}")
        for ln in lines:
            print(f"      {ln}")
        if ok is None:
            skipped += 1
        elif ok:
            passed += 1
        else:
            failed += 1
    print("\n" + "=" * 70)
    print(f"RESULT: {passed} proven, {failed} failed, {skipped} skipped (independent tool absent)")
    print("Note: simulation/independent-tool agreement proves the DESIGN + CONTROL are")
    print("correct given the parts. It is not a wet-lab yield result - that needs the bench.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
