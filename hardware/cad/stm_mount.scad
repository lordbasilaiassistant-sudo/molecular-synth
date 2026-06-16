// Molecular Synth v0 - parametric DIY STM scanner mount (OPTIONAL track)
// =======================================================================
// Atomic-resolution capability demonstrator after Dan Berard's open-source STM:
// a piezo buzzer disk is the XYZ scanner, a hand-cut Pt/Ir wire is the tip, a
// transimpedance amplifier reads the ~nA tunnelling current, a Teensy/Arduino
// runs the feedback. A hobby STM reliably resolves the atomic lattice of HOPG
// graphite - it is NOT a direct imager of soft, hydrated DNA origami (use the gel
// for routine origami QC). See docs/research/04-verification-gel-stm.md.
//
// This prints the rigid base + magnetic coarse-approach ramp that the inchworm /
// screw advance pushes the sample toward the tip. Dimensions in mm; print rigid
// (PETG/ASA) and add mass (steel plate) for vibration isolation.
//
//   openscad -D part=\"base\" -o base.stl stm_mount.scad   // part = base|ramp|tip_holder|all

/* [Geometry] */
base_d      = 70;
base_h      = 10;
piezo_d     = 27;   // 27 mm piezo buzzer disk
piezo_pocket= 1.5;
ramp_angle  = 6;    // shallow coarse-approach incline
tip_arm_h   = 28;

part = "all";

module base() {
    difference() {
        cylinder(h = base_h, d = base_d, $fn=120);
        // piezo scanner pocket (center)
        translate([0,0,base_h - piezo_pocket])
            cylinder(h = piezo_pocket + 1, d = piezo_d + 0.6, $fn=80);
        // wire routing slot
        translate([0,0,base_h-3]) cube([base_d, 4, 4], center=true);
        // three M3 isolation-foot holes
        for (a = [0:120:240])
            rotate([0,0,a]) translate([base_d/2 - 7, 0, -1])
                cylinder(h = base_h + 2, d = 3.2, $fn=24);
    }
}

// Shallow coarse-approach wedge: the sample slides down it toward the tip.
module ramp() {
    l = 40; w = 18; h = l * tan(ramp_angle);
    rotate([90,0,0])
        linear_extrude(height = w)
            polygon([[0,0],[l,0],[l,h]]);
}

module tip_holder() {
    // arm that clamps the Pt/Ir tip over the piezo center
    difference() {
        union() {
            cube([8, 8, tip_arm_h]);
            translate([0,0,tip_arm_h-6]) cube([26, 8, 6]);
        }
        // tip channel (vertical) at the far end, over scanner center
        translate([22, 4, tip_arm_h-7]) cylinder(h=8, d=1.0, $fn=20);
        // mounting hole
        translate([4,4,-1]) cylinder(h=tip_arm_h+2, d=3.2, $fn=24);
    }
}

if (part == "base" || part == "all") base();
if (part == "ramp" || part == "all") translate([base_d/2+10,0,0]) ramp();
if (part == "tip_holder" || part == "all") translate([-base_d/2-15,0,0]) tip_holder();
