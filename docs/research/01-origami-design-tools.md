# 01 — DNA Origami Fundamentals + Automated Shape→Scaffold-Routing Software

Research dossier for **Molecular Synth v0** — a desktop open-hardware rig that uses DNA self-assembly
(DNA origami) to manufacture atomically-precise nanostructures, plus a software compiler
(**shape → DNA staple recipe**).

> **Scope honesty up front.** DNA origami reliably makes **~10 nm to ~1 µm** structures (single particles;
> with hierarchical assembly, lattices/gigadalton objects). It does **NOT** make macroscopic objects, and it
> does **NOT** do Drexler-style diamondoid mechanosynthesis — that remains **simulation/theory only**, never
> experimentally demonstrated (see "North-star" section). Everything marked `demonstrated=true` below is an
> actual wet-lab result in the cited paper.

---

## 1. The scientific backbone (all peer-reviewed, all web-verified)

### 1.1 Rothemund 2006 — scaffolded DNA origami (the founding paper)
- **Citation:** Paul W. K. Rothemund, "Folding DNA to create nanoscale shapes and patterns," *Nature* **440**, 297–302 (2006). DOI: 10.1038/nature04586. <https://www.nature.com/articles/nature04586>
- **What it demonstrated (lab):** Folded a single ~7 kb single-stranded scaffold (M13) into arbitrary **2D** shapes
  (squares, stars, smiley faces, a map) by raster-filling the shape and adding ~200+ short "staple" oligos.
  Imaged by AFM. This is the canonical method the whole field is built on.
- **Key design numbers introduced:** scaffold raster-filled into rows of parallel helices; staples are ~32 nt
  (binding 2–3 scaffold segments); crossovers placed at periodic intervals; helices ~6 nm apart.

### 1.2 Douglas et al. 2009 — 3D origami + caDNAno
- **Citation:** Shawn M. Douglas, Hendrik Dietz, Tim Liedl, Björn Högberg, Franziska Graf, William M. Shih,
  "Self-assembly of DNA into nanoscale three-dimensional shapes," *Nature* **459**, 414–418 (2009).
  DOI: 10.1038/nature08016. <https://www.nature.com/articles/nature08016> (PMC: PMC2688462)
- **Companion software paper:** Douglas, Marblestone, Teerapittayanon, Vazquez, Church, Shih, "Rapid prototyping
  of three-dimensional DNA-origami shapes with caDNAno," *Nucleic Acids Research* **37**, 5001–5006 (2009).
  DOI: 10.1093/nar/gkp436. caDNAno: <https://cadnano.org/>
- **What it demonstrated (lab):** Extended origami to **3D** by stacking helices on a **honeycomb lattice**;
  built monolith, square nut, railed bridge, slotted/stacked cross, etc. **caDNAno** is the GUI CAD tool that
  made manual 3D design tractable — still the field-standard editor.

### 1.3 Ke et al. 2012 — DNA bricks (scaffold-free, modular "voxels")
- **Citation:** Yonggang Ke, Luvena L. Ong, William M. Shih, Peng Yin, "Three-Dimensional Structures
  Self-Assembled from DNA Bricks," *Science* **338**, 1177–1183 (2012). DOI: 10.1126/science.1227268.
  <https://www.science.org/doi/10.1126/science.1227268> (PubMed 23197527)
- **What it demonstrated (lab):** A **scaffold-free** alternative: 32-nt "bricks," each binding 4 neighbors
  like interlocking LEGO. From a master "molecular canvas" they removed/added bricks to sculpt **100+ distinct
  3D shapes** in a single annealing pot. Important because it's the "voxel compiler" mental model — a 3D shape
  is just a subset of bricks toggled on/off.

### 1.4 Benson et al. 2015 — polygonal mesh → DNA (vHelix)
- **Citation:** Erik Benson, Abdulmelik Mohammed, Johan Gardell, Sergej Masich, Eugen Czeizler, Pekka Orponen,
  Björn Högberg, "DNA rendering of polyhedral meshes at the nanoscale," *Nature* **523**, 441–444 (2015).
  DOI: 10.1038/nature14586. <https://www.nature.com/articles/nature14586>
- **Tool:** **vHelix**, an Autodesk Maya plug-in. <http://www.vhelix.org/>
- **What it demonstrated (lab):** Took **arbitrary closed polygonal meshes** and rendered them as
  wireframe DNA (ball, bottle, bunny, etc.). First time an artist's 3D mesh could be folded with minimal
  manual routing. Uses a relaxation/optimization to assign helices to mesh edges.

### 1.5 Veneziano et al. 2016 — DAEDALUS (fully automatic top-down routing) ★ core of the compiler
- **Citation:** Rémi Veneziano, Sakul Ratanalert, Kaiming Zhang, Fei Zhang, Hao Yan, Wah Chiu, Mark Bathe,
  "Designer nanoscale DNA assemblies programmed from the top down," *Science* **352**, 1534 (2016).
  DOI: 10.1126/science.aaf4388. <https://www.science.org/doi/10.1126/science.aaf4388> (PubMed 27229143)
- **Tool / code:** **DAEDALUS**; Python re-implementation **pyDAEDALUS** at <https://github.com/lcbb/pyDAEDALUS>.
- **What it demonstrated (lab):** **Fully automatic inverse design** — input is just a geometric mesh
  (PLY), output is the complete scaffold route + all staple sequences, with **no manual editing**. Built and
  characterized 45 wireframe objects (tetrahedron→icosahedron, cuboctahedron, nested cube, etc.) by cryo-EM/AFM.
  This is the algorithmic heart of a "shape→recipe" compiler.

### 1.6 Jun et al. 2019 — PERDIX / TALOS / (and METIS) automated wireframe suites
- **PERDIX (free-form 2D):** Hyungmin Jun, Fei Zhang, Tyson Shepherd, Sakul Ratanalert, Xiaodong Qi, Hao Yan,
  Mark Bathe, "Autonomously designed free-form 2D DNA origami," *Science Advances* **5**, eaav0655 (2019).
  DOI: 10.1126/sciadv.aav0655. <https://www.science.org/doi/10.1126/sciadv.aav0655>
  PERDIX = *Programmed Eulerian Routing for DNA Design using X-overs.*
- **TALOS (3D polyhedral, honeycomb edges):** Hyungmin Jun, Tyson R. Shepherd, Kaiming Zhang, William P.
  Bricker, Shanshan Li, Wah Chiu, Mark Bathe, "Automated Sequence Design of 3D Polyhedral Wireframe DNA Origami
  with Honeycomb Edges," *ACS Nano* **13**, 2083–2093 (2019). DOI: 10.1021/acsnano.8b08671. (PubMed 30605605)
- **METIS (2D, stiffer 6-helix-bundle / honeycomb edges):** Hyungmin Jun, Xiao Wang, William P. Bricker,
  Mark Bathe, "Automated sequence design of 2D wireframe DNA origami with honeycomb edges," *Nature
  Communications* **10**, 5419 (2019). DOI: 10.1038/s41467-019-13457-y.
  <https://www.nature.com/articles/s41467-019-13457-y>
- **ATHENA (unifying GUI + later rapid-prototyping):** Jun, Wang, Bricker, Jackson, Bathe, "Rapid prototyping
  of arbitrary 2D and 3D wireframe DNA origami," *Nucleic Acids Research* **49**, 10265–10274 (2021).
  DOI: 10.1093/nar/gkab762. GUI: <https://github.com/lcbb/athena>. METIS source: <https://github.com/hmjeon/METIS-pub>.
- **What they demonstrate (lab):** The Bathe-lab line that turns DAEDALUS into a usable toolchain — input a CAD
  geometry (PLY / SVG / IGES), get scaffold+staple sequences for DX-edge (PERDIX), 6HB-edge (METIS), or 3D
  honeycomb-edge (TALOS) wireframes, all validated by AFM/cryo-EM in the papers.

---

## 2. Design/simulation software stack (what the compiler actually wraps)

| Tool | Role | Open-source? | Install | Input → Output formats |
|---|---|---|---|---|
| **caDNAno** | Manual 2D/3D origami CAD (lattice editor) | Yes (BSD) | desktop / Autodesk Maya plug-in; `pip`-era forks exist | `.json` (caDNAno) |
| **scadnano** | Browser + scriptable port of caDNAno | Yes (MIT) | web app + `pip install scadnano` | `.sc` (scadnano JSON), exports caDNAno `.json`, oxDNA, oxView, IDT plate CSV |
| **vHelix** | Mesh→DNA (Maya plug-in) | Yes | Maya plug-in | `.ply` mesh → routed design |
| **pyDAEDALUS** | Top-down mesh→scaffold+staples | Yes | Python (clone repo) | `.ply` → caDNAno `.json` + staple sequence list |
| **PERDIX/TALOS/METIS/ATHENA** | Automated wireframe sequence design | Yes | Fortran/Python + GUI | `.ply`/`.svg`/`.iges` → scaffold+staple CSV, caDNAno `.json`, oxDNA |
| **oxDNA / oxpy** | Coarse-grained MD/MC validation of the design | Yes (GPL) | `git clone` + CMake `-DPython=1` → `oxpy`; optional CUDA GPU | `.top` + `.dat`/`.conf` (oxDNA topology+config) |
| **oxView** | Browser visualizer/editor of nanostructures | Yes | web (`sulcgroup/oxdna-viewer`) | reads oxDNA `.top/.dat`, `.oxview`; imports caDNAno via tacoxDNA |
| **tacoxDNA** | Format converter hub | Yes | web (tacoxdna.sissa.it) + Python | caDNAno/PDB/LAMMPS/cadnano↔oxDNA |
| **NUPACK** | Nucleic-acid thermodynamics / sequence design | Yes (academic) | `pip` (NUPACK 4) | sequences → MFE structure, pair probs, melt |
| **ViennaRNA** | Secondary-structure / folding energetics | Yes | `pip install ViennaRNA` / conda | sequence → structure/energy |

### 2.1 scadnano (Doty et al.)
- **Citation:** David Doty, Benjamin L. Lee, Tristan Stérin, "scadnano: A Browser-Based, Scriptable Tool for
  Designing DNA Nanostructures," *DNA 26* (LIPIcs vol. 174), 9:1–9:17 (2020). DOI: 10.4230/LIPIcs.DNA.2020.9.
  arXiv: 2005.11841. Web app: <https://scadnano.org/>. Python lib:
  <https://github.com/UC-Davis-molecular-computing/scadnano-python-package> (`pip install scadnano`).
- **Why it matters for the compiler:** It's the most automation-friendly editor — pure-Python scripting
  generates designs programmatically and exports directly to **IDT plate order files** and oxDNA. This is the
  natural "back end" for a shape→recipe compiler that needs to emit an orderable oligo plate.

### 2.2 oxDNA coarse-grained model (Ouldridge / Snodin / Šulc / Romano / Doye / Louis / Rovigatti)
- **Original model:** Thomas E. Ouldridge, Ard A. Louis, Jonathan P. K. Doye, "Structural, mechanical, and
  thermodynamic properties of a coarse-grained DNA model," *J. Chem. Phys.* **134**, 085101 (2011).
  DOI: 10.1063/1.3552946. arXiv: 1009.4480.
- **Sequence-dependent (oxDNA2):** P. Šulc, F. Romano, T. E. Ouldridge, L. Rovigatti, J. P. K. Doye, A. A.
  Louis, "Sequence-dependent thermodynamics of a coarse-grained DNA model," *J. Chem. Phys.* **137**, 135101
  (2012). DOI: 10.1063/1.4747335.
- **Modern code/JOSS:** Poppleton, Matthies, et al., "oxDNA: coarse-grained simulations of nucleic acids made
  simple," *JOSS* (2023). Code + docs: <https://github.com/lorenzo-rovigatti/oxDNA>,
  <https://lorenzo-rovigatti.github.io/oxDNA/>.
- **What it does:** Coarse-grained MD that predicts whether a designed origami will actually fold/be stable
  (it is **simulation**, not a wet-lab demonstration — used to validate designs before ordering oligos).

### 2.3 oxView (Poppleton et al.) + oxDNA.org webserver
- **Citation:** Erik Poppleton, Joakim Bohlin, Michael Matthies, Shuchi Sharma, Fei Zhang, Petr Šulc, "Design,
  optimization and analysis of large DNA and RNA nanostructures through interactive visualization, editing and
  molecular simulation," *Nucleic Acids Research* **48**, e72 (2020). DOI: 10.1093/nar/gkaa417.
- **Protocols paper:** Bohlin, Matthies, Poppleton, et al., "Design and simulation of DNA, RNA and hybrid
  protein–nucleic acid nanostructures with oxView," *Nature Protocols* **17**, 1762–1788 (2022).
  DOI: 10.1038/s41596-022-00688-5.
- **oxDNA.org server:** Poppleton et al., *Nucleic Acids Research* **49**, W491 (2021). DOI: 10.1093/nar/gkab324.
  <https://oxdna.org/> — run oxDNA in the browser with no install.

### 2.4 NUPACK (Zadeh et al.) and ViennaRNA
- **NUPACK:** J. N. Zadeh, C. D. Steenberg, J. S. Bois, B. R. Wolfe, M. B. Pierce, A. R. Khan, R. M. Dirks,
  N. A. Pierce, "NUPACK: Analysis and design of nucleic acid systems," *J. Comput. Chem.* **32**, 170–173
  (2011). DOI: 10.1002/jcc.21596. (Companion design paper: Zadeh, Wolfe, Pierce, *JCC* **32**, 439, 2011,
  DOI 10.1002/jcc.21633.) NUPACK 4 is `pip`-installable.
- **Use in compiler:** sequence-level QC — check staples don't form strong hairpins/dimers, estimate melting,
  optionally redesign sequences to hit a target ensemble defect.

---

## 3. The top-down mesh→scaffold-routing ALGORITHM (the compiler core)

This is the piece the software compiler must implement. Distilled from DAEDALUS (Veneziano 2016) and
PERDIX/TALOS (Jun 2019):

1. **Input:** a closed surface as a polygonal mesh (`.ply`) — vertices `V`, edges `E`, faces `F`.
2. **Edge → duplex assignment:** each mesh edge becomes one (DX, 2-duplex) or more (6HB) parallel DNA
   duplexes. Edge length is quantized to an integer number of helical turns; **B-DNA ≈ 10.5 bp/turn**, so an
   edge of *n* turns ≈ `round(10.5 × n)` bp (DAEDALUS uses multiples of ~10.5 to keep crossovers in phase).
3. **Scaffold routing = spanning tree:** A single scaffold strand must traverse the whole object exactly once.
   DAEDALUS builds a **spanning tree of the mesh** (Prim's algorithm). The spanning-tree edges get a
   **scaffold double-crossover**; non-tree edges are bridged so the scaffold makes **one continuous closed
   route** — equivalent to finding an **Eulerian circuit** of the (doubled) edge graph. Doubling every edge
   guarantees all vertices have even degree ⇒ an Eulerian circuit always exists.
4. **A-trail (for some wireframe schemes):** an **A-trail** is an Eulerian circuit that always turns to the
   "next" edge around each vertex (a non-crossing/face-respecting Eulerian circuit). A-trails let the scaffold
   route a wireframe with a **single scaffold and no scaffold crossovers between layers**, simplifying folding
   (used by vHelix-style and square-lattice wireframe routing; ref: Mohammed/Czeizler/Orponen on Eulerian
   circuits with turning costs; "Computer-Aided Design of A-Trail Routed Wireframe DNA Nanostructures with
   Square Lattice Edges," PMC10100577).
5. **Staple generation:** staples are laid antiparallel to the scaffold, ~**32 nt** typical, each crossing
   between adjacent duplexes at **crossover points**. Crossover spacing in lattice origami is periodic:
   honeycomb lattice ~7 bp (≈0.66 turn) between crossovers; square lattice ~8 bp; edges/seams placed so a
   crossover lands every ~half-to-three-quarter turn. Staples are broken to be ~18–50 nt and to have adequate
   binding domains (≥~8 nt per domain) for thermal stability.
6. **Sequence assignment:** the scaffold sequence (M13, see §4) is threaded along the route; each staple's
   sequence is the Watson–Crick complement of the scaffold segments it covers. Optional NUPACK/ViennaRNA pass
   flags problematic staples.
7. **Output:** caDNAno/scadnano `.json` for inspection, oxDNA `.top/.dat` for simulation, and a **staple list
   (sequence + well position) as a plate CSV** ready to order.

---

## 4. The M13mp18 scaffold (the "feedstock" the compiler threads)

- **What it is:** the circular single-stranded genome of bacteriophage **M13mp18**, **7,249 nucleotides**, the
  canonical origami scaffold (Rothemund 2006 onward). Variants exist at 7,308 / 7,560 / 7,704 / 8,064 / 8,634 nt.
- **Where the sequence is canonically obtained:** GenBank accession for M13mp18 RF is **X02513** (M13mp18 is
  the M13 cloning vector lineage); the 7,249-nt ssDNA scaffold sequence is distributed with caDNAno/scadnano
  as a built-in scaffold string and is also published in the Rothemund 2006 supplement. (Vendor: NEB N4040;
  Tilibit/now part of community suppliers historically distributed p7249.)
- **Orderable as a consumable:** **NEB N4040 "M13mp18 Single-stranded DNA," 10 µg (~$52, VWR/Fisher/NEB).**
  10 µg ≈ ~4 nmol of a 7249-nt strand — enough for many small folding reactions.

---

## 5. Buildable rig — Molecular Synth v0 (hobbyist, USA, < $1500 rig target)

**Honest framing of the wet process:** DNA origami folding is shockingly low-tech to *run* (the design is the
hard part). A folding reaction = mix scaffold + staples in Mg²⁺ buffer (TAE-Mg / "folding buffer"), then run a
**thermal anneal ramp** (heat to ~90–95 °C, cool slowly to ~20 °C over 1–16 h). Readout/QC = **agarose gel
electrophoresis** (does it migrate as a folded band?) and, for actual shape confirmation, **AFM or TEM** — AFM
is the only nm-resolution imager remotely in hobby reach, and even a used one usually blows the budget, so v0
treats imaging as "send-out / collaborator" and proves folding by gel mobility.

The two rig essentials a hobbyist must own: **(a) a programmable thermal ramp** and **(b) gel
electrophoresis**. Both are repurposable/affordable:

- **Thermal ramp (the only truly custom build):** a **Peltier (TEC) + aluminum block + Arduino PID** controller
  is the standard DIY thermocycler — exactly the OpenPCR / "coffee-cup PCR" pattern. For origami you don't even
  need fast cycling, just a smooth slow cool, which a sous-vide-grade TEC controller does well.
- **Gel + power supply:** a sub-$200 all-in-one education gel kit covers QC.
- **All-in-one fallback:** **Bento Lab** ($1,999) bundles thermocycler+centrifuge+gel+transilluminator but is
  *over* the $1,500 rig budget; listed as optional.

See `parts` in the structured payload for orderable URLs/prices. Consumables (scaffold, staples, buffer,
stain) are counted separately from the rig budget.

---

## 6. North-star vs. demonstrated (ruthless honesty)

- **Demonstrated today:** programmable self-assembly of **single nanostructures 10 nm–1 µm**, wireframe
  polyhedra, 3D lattices, nm-precise placement of dyes/proteins/nanoparticles on an origami "breadboard."
  Higher-order: gigadalton assemblies and crystalline lattices via hierarchical origami (Wagenbauer et al.,
  *Nature* 2017; Tikhomirov et al., *Nature* 2017 — fractal/µm-scale arrays). Still **nano-to-micro**, not
  macroscopic.
- **NOT demonstrated (north-star / simulation only):** Drexler-style **diamondoid mechanosynthesis** — building
  stiff covalent solids atom-by-atom with positionally-controlled tooltips. This exists only in **theory/DFT/MD**
  (e.g., tooltip-reaction DFT studies), **never an experimental lab demonstration**. Any "atomically-precise
  manufacturing of hard materials" claim for Molecular Synth must be labeled `demonstrated=false`.
- **Therefore the compiler's honest promise:** "shape (mesh) → orderable DNA staple recipe that self-assembles
  a ~10 nm–1 µm scaffolded nanostructure," validated in silico by oxDNA and in vitro by gel. Not a matter
  compiler.

---

## 7. Code facts the software compiler needs (cheat-sheet)

- **Pip/conda installable:** `scadnano` (pip), `oxpy`/oxDNA (CMake build, optional CUDA), `ViennaRNA` (pip/conda),
  NUPACK 4 (pip, academic license). pyDAEDALUS / METIS / ATHENA = clone-from-GitHub (Python/Fortran).
- **File formats:** caDNAno `.json`; scadnano `.sc` (JSON); oxDNA `.top` (topology) + `.dat`/`.conf`
  (configuration); `.oxview` (richer JSON w/ colors, strand names, base pairs); mesh input `.ply`
  (also SVG/IGES for ATHENA/METIS); structural `.pdb`; IDT plate order = CSV (name, sequence, well, scale).
- **Conversions:** tacoxDNA (caDNAno/PDB/LAMMPS ↔ oxDNA); scadnano exports caDNAno+oxDNA+oxView+IDT CSV.
- **Routing algorithm:** mesh → spanning tree (Prim) → double edges → Eulerian circuit (A-trail variant for
  non-crossing wireframe) → scaffold route → antiparallel staples at periodic crossovers.
- **Magic numbers:** B-DNA **10.5 bp/turn**; staples **~32 nt** (18–50 nt range, ≥~8 nt per binding domain);
  crossover spacing honeycomb **~7 bp**, square lattice **~8 bp**; inter-helix spacing ~2.5–2.6 nm (lattice).
- **Scaffold:** **M13mp18, 7,249 nt** (GenBank X02513 lineage; built into caDNAno/scadnano as p7249).
- **Validation pass:** oxDNA MD (CPU or CUDA GPU) for fold stability; NUPACK/ViennaRNA for staple hairpin/dimer
  and melt QC.

---

## Sources (key URLs)
- Rothemund 2006: <https://www.nature.com/articles/nature04586>
- Douglas 2009 (3D): <https://www.nature.com/articles/nature08016> · caDNAno: <https://cadnano.org/>
- Ke 2012 (bricks): <https://www.science.org/doi/10.1126/science.1227268>
- Benson 2015 (vHelix): <https://www.nature.com/articles/nature14586> · <http://www.vhelix.org/>
- Veneziano 2016 (DAEDALUS): <https://www.science.org/doi/10.1126/science.aaf4388> · <https://github.com/lcbb/pyDAEDALUS>
- Jun 2019 PERDIX: <https://www.science.org/doi/10.1126/sciadv.aav0655> · TALOS: 10.1021/acsnano.8b08671 · METIS: <https://www.nature.com/articles/s41467-019-13457-y> · ATHENA: <https://github.com/lcbb/athena>
- scadnano: <https://scadnano.org/> · <https://github.com/UC-Davis-molecular-computing/scadnano-python-package>
- oxDNA: <https://github.com/lorenzo-rovigatti/oxDNA> · <https://lorenzo-rovigatti.github.io/oxDNA/> · oxView: <https://github.com/sulcgroup/oxdna-viewer> · oxDNA.org: <https://oxdna.org/>
- NUPACK: <https://onlinelibrary.wiley.com/doi/10.1002/jcc.21596>
- M13mp18 scaffold (consumable): NEB N4040 <https://www.neb.com/products/n4040-m13mp18-single-stranded-dna>
- miniPCR: <https://www.minipcr.com/product/minipcr-mini8x-thermal-cycler/> · Bento Lab: <https://bento.bio/product/bento-lab-rs/>
- IVYX gel system: <https://www.amazon.com/Electrophoresis-System-Power-Supply-Timer/dp/B0B2ZSRG2Z>
