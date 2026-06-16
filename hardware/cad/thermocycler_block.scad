// Molecular Synth v0 - parametric Peltier folding-block enclosure
// ================================================================
// Stack (bottom -> top):  heatsink + fan  |  Peltier TEC1-12706 (40x40 mm)  |
// aluminium block drilled for 0.2 mL PCR tubes  |  this printed insulating collar
// + lid that clamps the stack and holds the NTC thermistor against the block.
//
// The Peltier is driven bidirectionally (BTS7960 H-bridge) by thermocycler.ino so
// the block both heats to 90 C and slow-cools to 20 C - the origami folding ramp.
// Print in PETG (better >60 C than PLA) or ASA. Dimensions in mm.
//
//   openscad -D part=\"collar\" -o collar.stl thermocycler_block.scad
//   part = \"collar\" | \"lid\" | \"all\"

/* [Peltier + block] */
pelt        = 40;     // Peltier edge (TEC1-12706 is 40x40x3.x mm)
block_x     = 40;
block_y     = 40;
block_h     = 18;     // aluminium block height
wall        = 4;
collar_h    = 22;

/* [Tube holes - for reference / a printable block if no aluminium] */
n_tubes     = 6;
tube_top_d  = 6.2;    // 0.2 mL tube top dia
tube_bot_d  = 2.8;
tube_depth  = 16;

/* [Thermistor] */
therm_d     = 4.2;    // channel for a glass-bead/epoxy NTC

part = "all";

module insulating_collar() {
    difference() {
        cube([block_x + 2*wall, block_y + 2*wall, collar_h]);
        // pocket the aluminium block sits in
        translate([wall, wall, wall])
            cube([block_x, block_y, collar_h]);
        // thermistor channel into the block pocket from the side
        translate([-1, wall + block_y/2, wall + block_h/2])
            rotate([0,90,0]) cylinder(h = wall + 2, d = therm_d, $fn=24);
        // wire exit slot
        translate([block_x/2, -1, collar_h-5]) cube([8, wall+2, 6]);
    }
}

module clamp_lid() {
    difference() {
        cube([block_x + 2*wall, block_y + 2*wall, wall + 6]);
        // tube access holes (align over the aluminium block bores)
        span = block_x - 8;
        pitch = span / n_tubes;
        for (i = [0 : n_tubes-1])
            translate([wall + 4 + i*pitch, block_y/2 + wall, -1])
                cylinder(h = wall + 8, d = tube_top_d, $fn=32);
    }
}

// Optional: a fully-printable aluminium-free block is NOT recommended (plastic is a
// poor conductor); use a drilled aluminium bar. This module documents the bore map.
module reference_block() {
    difference() {
        cube([block_x, block_y, block_h]);
        span = block_x - 8;
        pitch = span / n_tubes;
        for (i = [0 : n_tubes-1])
            translate([4 + i*pitch, block_y/2, block_h - tube_depth + 0.1])
                cylinder(h = tube_depth + 1, d1 = tube_bot_d, d2 = tube_top_d, $fn=32);
    }
}

if (part == "collar" || part == "all") insulating_collar();
if (part == "lid"    || part == "all") translate([0, -block_y - 20, 0]) clamp_lid();
if (part == "block_ref") reference_block();
