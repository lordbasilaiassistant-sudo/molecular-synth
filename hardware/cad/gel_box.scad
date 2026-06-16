// Molecular Synth v0 - parametric DIY agarose gel-electrophoresis box
// ====================================================================
// Verify a fold: well-folded DNA origami runs as one tight band, distinct from
// the scaffold-only lane (Castro et al., Nat. Methods 2011; Stahl et al.,
// Angew. Chem. 2014). 3D-print this box (PLA/PETG), add stainless or platinum
// wire electrodes, run in 1x TAE + 12.5 mM MgCl2 at ~60-90 V on ice.
//
// Render the parts:  openscad -D part=\"buffer\" -o buffer.stl gel_box.scad
//                    part = \"buffer\" | \"tray\" | \"comb\" | \"all\"
//
// All dimensions in millimetres. Edit the parameters block to fit your gel size.

/* [Box] */
gel_len      = 80;    // casting tray inner length (run direction)
gel_wid      = 60;    // casting tray inner width
gel_thk      = 8;     // gel thickness
wall         = 3;     // wall thickness
buffer_extra = 22;    // electrode chamber length at each end
floor_thk    = 3;

/* [Comb] */
n_wells      = 8;
well_wid     = 5;
well_thk     = 1.2;   // tooth thickness -> well width in gel
comb_depth   = 6;     // how deep teeth dip into the gel
comb_handle  = 10;

/* [Electrodes] */
elec_d       = 1.6;   // wire / channel diameter (1.5 mm stainless TIG rod)
elec_z       = 4;     // height of electrode channel above floor

part = "all";

module buffer_chamber() {
    total_len = gel_len + 2*buffer_extra;
    total_wid = gel_wid + 2*wall;
    wall_h    = gel_thk + 12;
    difference() {
        // outer shell
        cube([total_len + 2*wall, total_wid, wall_h + floor_thk]);
        // inner cavity
        translate([wall, wall, floor_thk])
            cube([total_len, gel_wid, wall_h + 1]);
    }
    // casting-tray ledges (tray drops onto these, leaving electrode chambers open)
    for (x = [wall + buffer_extra, wall + buffer_extra + gel_len - 4])
        translate([x, wall, floor_thk])
            cube([4, gel_wid, 3]);
    // electrode channels (push wire through both side walls at each end)
    for (x = [wall + buffer_extra/2, wall + buffer_extra*1.5 + gel_len])
        translate([x, -1, floor_thk + elec_z])
            rotate([-90,0,0]) cylinder(h = total_wid + 2, d = elec_d, $fn=24);
}

module casting_tray() {
    difference() {
        cube([gel_len, gel_wid, gel_thk + floor_thk]);
        translate([wall, wall, floor_thk])
            cube([gel_len - 2*wall, gel_wid - 2*wall, gel_thk + 1]);
    }
    // open ends (dam removed before running) modelled as removable end caps
    // -> print two loose end dams:
    translate([0, gel_wid + 6, 0]) cube([2.5, gel_wid, gel_thk + floor_thk]);
    translate([6, gel_wid + 6, 0]) cube([2.5, gel_wid, gel_thk + floor_thk]);
}

module comb() {
    span = gel_wid - 2*wall - 6;
    pitch = span / n_wells;
    // handle bar
    translate([-2, 0, 0]) cube([well_thk + 4, span, comb_handle]);
    // teeth
    for (i = [0 : n_wells - 1])
        translate([0, i*pitch + (pitch - well_wid)/2, -comb_depth])
            cube([well_thk, well_wid, comb_depth + 1]);
}

if (part == "buffer" || part == "all") buffer_chamber();
if (part == "tray"   || part == "all") translate([0, -gel_wid - 20, 0]) casting_tray();
if (part == "comb"   || part == "all") translate([0, -gel_wid - 90, comb_depth]) comb();
