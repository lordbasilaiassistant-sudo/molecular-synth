"""
Write the compiled design to standard, orderable formats.

Always emitted:
  scaffold.fasta        the scaffold route (5'->3')
  staples.csv           ordered oligos: name, well, sequence, length, Tm, GC, flags
  staples_idt_plate.txt  IDT-ready plate upload (Well / Name / Sequence, tab-delimited)
  design.json           native full design (routing + staples + metadata)
  design.top            oxDNA topology (run oxDNA after adding coordinates)
Optional (only if the package is importable):
  design.sc             scadnano design (best-effort wireframe layout)
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


def write_scadnano(outdir, routing, staples):
    """Best-effort scadnano export (one helix per edge). Returns path or None.
    Never raises - the core pipeline does not depend on scadnano being installed."""
    try:
        import scadnano as sc  # type: ignore
    except Exception:
        return None
    try:
        # one helix per edge-traversal segment; lay each scaffold domain as a forward
        # strand (best-effort schematic for viewing in scadnano.org, not production
        # crossover geometry -- relax in oxDNA for that).
        segs = routing.segments
        n_helices = max(1, len(segs))
        helix_len = max((s.bp for s in segs), default=64) + 8
        design = sc.Design(helices=[sc.Helix(max_offset=helix_len) for _ in range(n_helices)],
                           grid=sc.square)
        for h, seg in enumerate(segs):
            design.draw_strand(h, 0).move(max(1, seg.bp)).with_sequence(seg.seq)
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

    sc_path = write_scadnano(outdir, routing, staples)
    if sc_path:
        written["design.sc"] = sc_path
    return written
