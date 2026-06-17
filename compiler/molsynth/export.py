"""
Write the compiled design to standard, orderable formats.

Always emitted:
  scaffold.fasta        the scaffold route (5'->3')
  staples.csv           ordered oligos: name, well, sequence, length, Tm, GC, flags
  staples_idt_plate.txt  IDT-ready plate upload (Well / Name / Sequence, tab-delimited)
  design.json           native full design (routing + staples + metadata)
  design.top            oxDNA topology (run oxDNA after adding coordinates)
  design_cadnano.json   caDNAno v2 legacy design (-> CanDo / oxDNA; topology verified)
Optional (only if the package is importable):
  design.sc             scadnano design (scaffold + base-paired staples; strand topology)
"""

from __future__ import annotations

import json
import os

from . import sequences as sq
from . import structure3d

OXDNA_UNIT_ANG = 8.518   # 1 oxDNA length unit ~ 0.8518 nm = 8.518 angstrom


def _w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_fasta(outdir, routing):
    path = os.path.join(outdir, "scaffold.fasta")
    seq = routing.scaffold_seq
    body = "\n".join(seq[i:i + 70] for i in range(0, len(seq), 70))
    _w(path, f">{routing.scaffold_name}_route len={len(seq)} synthetic={routing.synthetic}\n{body}\n")
    return path


def write_staples_csv(outdir, staples):
    path = os.path.join(outdir, "staples.csv")
    cols = ["name", "well", "sequence", "order_sequence", "handle", "guest", "length",
            "tm_C", "gc", "max_run", "repeats", "hairpin", "crossovers", "offtarget",
            "scaffold_start", "scaffold_end"]
    lines = [",".join(cols)]
    for s in staples:
        lines.append(",".join(str(x) for x in [
            s.name, s.well, s.seq, s.order_seq, s.handle, s.guest, s.length, s.tm_C, s.gc,
            s.max_run, s.repeats, s.hairpin, s.crossovers, s.offtarget,
            s.scaffold_start, s.scaffold_end,
        ]))
    _w(path, "\n".join(lines) + "\n")
    return path


def write_idt_plate(outdir, staples):
    """Tab-delimited Well/Name/Sequence — the IDT bulk plate-upload format."""
    path = os.path.join(outdir, "staples_idt_plate.txt")
    lines = ["Well Position\tName\tSequence"]
    for s in staples:
        lines.append(f"{s.well}\t{s.name}\t{s.order_seq}")
    _w(path, "\n".join(lines) + "\n")
    return path


def write_opool(outdir, staples, pool_name="molsynth_pool"):
    """IDT oPools bulk-input (Pool name / Sequence) - the cheap pooled-synthesis order
    (~$200 vs ~$750 for an addressable plate; see docs/research/05). One tube, not
    individually addressable - best for a first proof-of-fold."""
    path = os.path.join(outdir, "staples_opool.txt")
    lines = ["Pool name\tSequence"]
    for s in staples:
        lines.append(f"{pool_name}\t{s.order_seq}")
    _w(path, "\n".join(lines) + "\n")
    return path


def write_design_json(outdir, design, routing, staples):
    path = os.path.join(outdir, "design.json")
    obj = {
        "meta": design,
        "scaffold": {
            "name": routing.scaffold_name,
            "synthetic": routing.synthetic,
            "len_used": routing.scaffold_len_used,
            "sequence": routing.scaffold_seq,
        },
        "edges_bp": {f"{a}-{b}": v for (a, b), v in routing.edge_bp.items()},
        "segments": [
            {"order": s.order, "arc": list(s.arc), "edge": list(s.edge),
             "bp": s.bp, "scaffold_start": s.scaffold_start}
            for s in routing.segments
        ],
        "staples": [
            {"name": s.name, "well": s.well, "seq": s.seq, "order_seq": s.order_seq,
             "handle": s.handle, "guest": s.guest, "length": s.length,
             "tm_C": s.tm_C, "gc": s.gc, "crossovers": s.crossovers}
            for s in staples
        ],
    }
    _w(path, json.dumps(obj, indent=2))
    return path


def write_oxdna_topology(outdir, routing, staples):
    """Emit a valid oxDNA legacy .top (connectivity only) to design_topology.top.
    The pipeline uses write_oxdna() (consistent topology+config -> design.top); this
    standalone writer uses a DISTINCT filename so the two can never clobber."""
    path = os.path.join(outdir, "design_topology.top")
    strands = [routing.scaffold_seq] + [s.seq for s in staples]
    n = sum(len(s) for s in strands)
    lines = [f"{n} {len(strands)}"]
    gi = 0
    for sid, seq in enumerate(strands, start=1):
        # list 3'->5' (oxDNA convention: first listed nt is the 3' end)
        rev = seq[::-1]
        m_last = len(rev) - 1
        for m, base in enumerate(rev):
            n3 = gi - 1 if m > 0 else -1
            n5 = gi + 1 if m < m_last else -1
            lines.append(f"{sid} {base} {n3} {n5}")
            gi += 1
    _w(path, "\n".join(lines) + "\n")
    return path


def write_oxdna(outdir, nucs, box):
    """Write a CONSISTENT oxDNA topology (design.top) + configuration (conf.dat) from
    the ordered 3D nucleotide list, so the design can be visualised in oxView and
    relaxed/simulated in oxDNA.

    conf.dat is a STARTING configuration: base pairs are placed at their B-DNA
    equilibrium (backbones outside, bases meeting at the axis), but vertex-junction
    backbone bonds are over-stretched by construction. Run oxDNA's force-capped
    relaxation FIRST (sim_type=MD or MC with a small dt and `max_backbone_force`, i.e.
    the documented min->relax protocol) before any production run, or it will not be
    at equilibrium. See https://lorenzo-rovigatti.github.io/oxDNA/ (relaxation)."""
    nstrands = max((n.strand for n in nucs), default=0)
    top = [f"{len(nucs)} {nstrands}"]
    for n in nucs:
        top.append(f"{n.strand} {n.base} {n.n3} {n.n5}")
    top_path = os.path.join(outdir, "design.top")
    _w(top_path, "\n".join(top) + "\n")

    conf = [f"t = 0", f"b = {box:.4f} {box:.4f} {box:.4f}", "E = 0 0 0"]
    for n in nucs:
        p, a1, a3 = n.pos, n.a1, n.a3
        conf.append(
            f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} "
            f"{a1[0]:.4f} {a1[1]:.4f} {a1[2]:.4f} "
            f"{a3[0]:.4f} {a3[1]:.4f} {a3[2]:.4f} 0 0 0 0 0 0")
    conf_path = os.path.join(outdir, "conf.dat")
    _w(conf_path, "\n".join(conf) + "\n")
    return top_path, conf_path


def write_ply(outdir, mesh):
    """Emit the input shape as an ASCII PLY mesh — the format the reference automated
    wireframe-design tools (PERDIX/DAEDALUS/TALOS/ATHENA) consume. This is the honest
    bridge to a FABRICATION-GRADE design: run the same shape through those tools to get
    production crossover geometry, and cross-check against this compiler's output."""
    path = os.path.join(outdir, "shape.ply")
    lines = ["ply", "format ascii 1.0",
             f"element vertex {len(mesh.vertices)}",
             "property float x", "property float y", "property float z",
             f"element face {len(mesh.faces)}",
             "property list uchar int vertex_indices", "end_header"]
    for v in mesh.vertices:
        lines.append(f"{v[0]} {v[1]} {v[2]}")
    for f in mesh.faces:
        lines.append(f"{len(f)} " + " ".join(str(int(i)) for i in f))
    _w(path, "\n".join(lines) + "\n")
    return path


def write_oxdna_inputs(outdir, salt_M=0.5, temp_c=20):
    """Emit ready-to-run oxDNA relaxation input files. conf.dat is a STARTING config
    with over-stretched vertex-junction backbones; the documented fix is a two-step
    force-capped relaxation: (1) energy minimisation, then (2) short MD with a capped
    backbone force. Run:  oxDNA oxdna_min.input   then   oxDNA oxdna_relax.input."""
    common = (f"interaction_type = DNA2\n"
              f"salt_concentration = {salt_M}\n"
              f"T = {temp_c}C\n"
              f"topology = design.top\n"
              f"backend = CPU\n")
    min_input = (
        "##### oxDNA energy minimisation (step 1 of relaxation) #####\n"
        "sim_type = min\n"
        "steps = 2000\n"
        "conf_file = conf.dat\n"
        "lastconf_file = min.dat\n"
        "trajectory_file = min_trajectory.dat\n"
        "energy_file = min_energy.dat\n"
        "print_conf_interval = 200\n"
        "print_energy_every = 200\n"
        "restart_step_counter = 1\n"
        + common)
    relax_input = (
        "##### oxDNA force-capped MD relaxation (step 2 of relaxation) #####\n"
        "sim_type = MD\n"
        "steps = 100000\n"
        "dt = 0.003\n"
        "thermostat = brownian\n"
        "newtonian_steps = 103\n"
        "diff_coeff = 2.5\n"
        "max_backbone_force = 5.\n"
        "max_backbone_force_far = 10.\n"
        "conf_file = min.dat\n"
        "lastconf_file = relaxed.dat\n"
        "trajectory_file = relax_trajectory.dat\n"
        "energy_file = relax_energy.dat\n"
        "print_conf_interval = 10000\n"
        "print_energy_every = 10000\n"
        "restart_step_counter = 1\n"
        "refresh_vel = 1\n"
        + common)
    p1 = os.path.join(outdir, "oxdna_min.input")
    p2 = os.path.join(outdir, "oxdna_relax.input")
    _w(p1, min_input)
    _w(p2, relax_input)
    return p1, p2


_PDB_RES = {"A": "DA", "T": "DT", "G": "DG", "C": "DC"}
_PDB_CHAINS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def write_pdb(outdir, nucs):
    """One pseudo-atom (backbone P) per nucleotide -> opens in PyMOL/ChimeraX/Mol*.
    A coarse but universal way to eyeball the folded shape."""
    path = os.path.join(outdir, "structure.pdb")
    lines = ["REMARK  Molecular Synth v0 coarse structure (1 bead/nucleotide)"]
    serial = 0
    cur_strand = None
    resseq = 0
    for n in nucs:
        serial += 1
        if n.strand != cur_strand:          # restart residue numbering per chain
            cur_strand, resseq = n.strand, 0
        resseq += 1
        chain = _PDB_CHAINS[(n.strand - 1) % len(_PDB_CHAINS)]
        res = _PDB_RES.get(n.base, "DN")
        x, y, z = (c * OXDNA_UNIT_ANG for c in n.pos)
        rs = (resseq % 10000) or 1
        lines.append(
            f"ATOM  {serial % 100000:>5} {'P':^4} {res:>3} {chain}{rs:>4}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}{1.0:6.2f}{0.0:6.2f}          {'P':>2}")
    lines.append("END")
    _w(path, "\n".join(lines) + "\n")
    return path


def write_cadnano(outdir, routing, staples):
    """Emit a caDNAno v2 legacy JSON (design_cadnano.json), one virtual helix per
    scaffold segment. caDNAno is the most widely used origami CAD and the entry point to
    the CanDo finite-element shape/flexibility predictor and several oxDNA converters, so
    this is real interoperability.

    Each base carries the caDNAno [5'_vh, 5'_idx, 3'_vh, 3'_idx] pointer 4-tuple. The
    scaffold threads helix 0 -> 1 -> ... -> back to 0 as one closed loop (M13 is circular);
    each staple lies on the antiparallel staple strand (5'->3' = decreasing scaffold
    position), crossing helices wherever it bridges a vertex.

    HONEST SCOPE: this is a faithful encoding of the STRAND TOPOLOGY (scaffold route +
    staple breakpoints + base pairing) in a linear/schematic lattice layout -- NOT
    production 2D helix placement with in-phase crossovers. The topology is verified by an
    independent round-trip decoder (cadnano_decode -> proofs), but it is not GUI-tested in
    caDNAno itself. Apply the scaffold (scaffold.fasta) / staple (staples.csv) sequences in
    the tool; relax in oxDNA / predict in CanDo for fabrication-grade geometry."""
    segs = routing.segments
    if not segs:
        return None
    M = len(segs)
    L = max(s.bp for s in segs)
    num = [2 * i for i in range(M)]               # helix number per order (all even: scaf +idx)
    pos2hi = {}                                   # global scaffold pos -> (order, idx)
    for s in segs:
        for idx in range(s.bp):
            pos2hi[s.scaffold_start + idx] = (s.order, idx)

    scaf = [[[-1, -1, -1, -1] for _ in range(L)] for _ in range(M)]
    for s in segs:
        o, bp = s.order, s.bp
        prevo, nexto = (o - 1) % M, (o + 1) % M
        for idx in range(bp):
            p5 = (num[o], idx - 1) if idx > 0 else (num[prevo], segs[prevo].bp - 1)
            p3 = (num[o], idx + 1) if idx < bp - 1 else (num[nexto], 0)
            scaf[o][idx] = [p5[0], p5[1], p3[0], p3[1]]

    stap = [[[-1, -1, -1, -1] for _ in range(L)] for _ in range(M)]
    palette = [0x0066CC, 0xCC0000, 0x00AA00, 0xAA00AA, 0xDDAA00, 0x00AAAA, 0xAA5500, 0x5500AA]
    stap_colors = [[] for _ in range(M)]
    for si, st in enumerate(staples):
        start, end = st.scaffold_start, st.scaffold_end
        for g in range(start, end):
            o, idx = pos2hi[g]
            p5 = pos2hi[g + 1] if (g + 1) < end else None   # toward 5' = higher scaffold pos
            p3 = pos2hi[g - 1] if (g - 1) >= start else None  # toward 3' = lower scaffold pos
            a = [num[p5[0]], p5[1]] if p5 else [-1, -1]
            b = [num[p3[0]], p3[1]] if p3 else [-1, -1]
            stap[o][idx] = [a[0], a[1], b[0], b[1]]
        o5, idx5 = pos2hi[end - 1]                          # 5' end of the staple
        stap_colors[o5].append([idx5, palette[si % len(palette)]])

    vstrands = []
    for s in segs:
        o = s.order
        vstrands.append({
            "row": o, "col": 0, "num": num[o],
            "scaf": scaf[o], "stap": stap[o],
            "loop": [0] * L, "skip": [0] * L,
            "scafLoop": [], "stapLoop": [],
            "stap_colors": stap_colors[o],
        })
    obj = {"name": (routing.scaffold_name or "design") + ".json", "vstrands": vstrands}
    path = os.path.join(outdir, "design_cadnano.json")
    _w(path, json.dumps(obj))
    return path


def cadnano_decode(obj):
    """Independent reader: walk the caDNAno pointer arrays back into strands so the export
    can be VERIFIED (not trusted). Returns a report: the scaffold reconstructs as one
    closed loop of N bases, the staples reconstruct as K linear strands that partition the
    complementary bases exactly, and every pointer is reciprocal. Used by the round-trip
    proof + test. Pure topology (caDNAno JSON stores connectivity, not base letters)."""
    V = {v["num"]: v for v in obj["vstrands"]}
    empty = [-1, -1, -1, -1]
    scaf_occ, stap_occ = set(), set()
    for n, v in V.items():
        for i, e in enumerate(v["scaf"]):
            if e != empty:
                scaf_occ.add((n, i))
        for i, e in enumerate(v["stap"]):
            if e != empty:
                stap_occ.add((n, i))

    def reciprocal(arr):
        for n, v in V.items():
            for i, e in enumerate(v[arr]):
                ph, pi, nh, ni = e
                if nh != -1 and (V[nh][arr][ni][0], V[nh][arr][ni][1]) != (n, i):
                    return False
                if ph != -1 and (V[ph][arr][pi][2], V[ph][arr][pi][3]) != (n, i):
                    return False
        return True

    # trace the scaffold by following 3' pointers; it should be one closed loop
    scaf_loop_len, scaf_closed = 0, False
    if scaf_occ:
        start = min(scaf_occ)
        seen, cur, guard = [], start, 0
        while True:
            seen.append(cur)
            nh, ni = V[cur[0]]["scaf"][cur[1]][2:4]
            if nh == -1:
                break
            cur = (nh, ni)
            if cur == start:
                scaf_closed = True
                break
            guard += 1
            if guard > len(scaf_occ) + 2:
                break
        scaf_loop_len = len(seen)
        scaf_closed = scaf_closed and set(seen) == scaf_occ

    # trace staples from their 5' ends (no 5' neighbour) following 3' pointers
    five_primes = [(n, i) for (n, i) in stap_occ if V[n]["stap"][i][0] == -1]
    covered, staple_lens = set(), []
    for sp in five_primes:
        cur, ln = sp, 0
        while cur is not None:
            covered.add(cur)
            ln += 1
            nh, ni = V[cur[0]]["stap"][cur[1]][2:4]
            cur = (nh, ni) if nh != -1 else None
        staple_lens.append(ln)

    return {
        "scaffold_closed_loop": scaf_closed,
        "scaffold_len": scaf_loop_len,
        "n_staples": len(five_primes),
        "staple_lens": sorted(staple_lens),
        "staples_partition_complement": covered == stap_occ and scaf_occ == stap_occ,
        "pointers_reciprocal": reciprocal("scaf") and reciprocal("stap"),
    }


def write_scadnano(outdir, routing, staples):
    """scadnano export. Returns path or None (never raises -- the core pipeline does not
    depend on scadnano being installed).

    Faithful STRAND TOPOLOGY, not 3D wireframe geometry. The scaffold is laid as ONE
    strand (flagged is_scaffold) running 5'->3' on the forward strand of a single helix;
    every staple is its own strand on the ANTIPARALLEL reverse strand over the exact
    scaffold range it reverse-complements. So `scadnano.Design.from_scadnano_file()` reads
    back exactly one scaffold + K base-paired staples with the right sequences -- a valid,
    editable origami you can open at scadnano.org. (The earlier version drew each scaffold
    segment as a SEPARATE forward strand with no scaffold flag and no staples, so scadnano
    saw N disconnected fragments and zero scaffold -- not a foldable design.)

    HONEST SCOPE: this is the hybridization topology on a linearized helix, NOT the folded
    3D shape or production crossover geometry -- the scaffold's closing loop (circular M13)
    is shown cut, and the wireframe edges are not spatially placed. For shape use the oxDNA
    (design.top/conf.dat) or PDB outputs, or caDNAno (design_cadnano.json); relax in oxDNA.
    """
    try:
        import scadnano as sc  # type: ignore
    except Exception:
        return None
    try:
        seq = routing.scaffold_seq
        S = len(seq)
        if S < 2:
            return None
        design = sc.Design(helices=[sc.Helix(max_offset=S + 1)], grid=sc.square)
        # scaffold: one forward strand spanning the whole route, flagged is_scaffold
        design.draw_strand(0, 0).move(S).as_scaffold().with_sequence(seq)
        # staples: each on the antiparallel reverse strand over its scaffold range, so it
        # base-pairs the scaffold exactly (staple.seq == revcomp(seq[start:end]))
        for st in staples:
            a, b = st.scaffold_start, st.scaffold_end
            if b - a < 1:
                continue
            design.draw_strand(0, b).move(-(b - a)).with_sequence(st.seq)
        design.write_scadnano_file(directory=outdir, filename="design.sc")
        return os.path.join(outdir, "design.sc")
    except Exception:
        return None


def write_all(outdir, design, mesh, routing, staples):
    os.makedirs(outdir, exist_ok=True)
    # 3D structure first, so its self-check lands in design.json.
    nucs, box = structure3d.build_structure(mesh, routing, staples)
    design["structure_check"] = structure3d.orthonormal_report(nucs)

    written = {
        "scaffold.fasta": write_fasta(outdir, routing),
        "staples.csv": write_staples_csv(outdir, staples),
        "staples_idt_plate.txt": write_idt_plate(outdir, staples),
        "staples_opool.txt": write_opool(outdir, staples,
                                         pool_name=design.get("design_name", "molsynth_pool")),
        "design.json": write_design_json(outdir, design, routing, staples),
    }
    # consistent oxDNA topology + configuration + a universal PDB
    top_path, conf_path = write_oxdna(outdir, nucs, box)
    written["design.top"] = top_path
    written["conf.dat"] = conf_path
    written["structure.pdb"] = write_pdb(outdir, nucs)
    mn, rx = write_oxdna_inputs(outdir, salt_M=0.5, temp_c=int(design.get("t_cold", 20)))
    written["oxdna_min.input"] = mn
    written["oxdna_relax.input"] = rx

    if mesh.faces:                      # PERDIX/DAEDALUS-ready mesh for fabrication-grade
        written["shape.ply"] = write_ply(outdir, mesh)
    cad_path = write_cadnano(outdir, routing, staples)   # caDNAno v2 -> CanDo / oxDNA
    if cad_path:
        written["design_cadnano.json"] = cad_path
    sc_path = write_scadnano(outdir, routing, staples)
    if sc_path:
        written["design.sc"] = sc_path
    return written
