"""
Water Synth presets + the machine's harvest/treat/dispense model.

"I want a glass of cold water" -> harvest water from ambient AIR by Peltier condensation
(atmospheric water generation), filter + UV-treat it to potable, set temperature, dispense.

HONEST SCOPE: this HARVESTS and TREATS water from the air and a reservoir; it does NOT
materialise matter from energy. The lived experience ("ask, drinkable water appears") is
real and cheap today. The energy->matter replicator is north-star (see ../../docs/vision.md).

Why it matters: atmospheric water generation is a real humanitarian technology -- clean
water from air where there is none. Cited demonstrations:
  * Kim, H. et al. "Water harvesting from air with metal-organic frameworks powered by
    natural sunlight." Science 356, 430-434 (2017).  (water from <20% RH desert air)
  * Commercial/DIY condensation AWG (a Peltier or refrigeration coil below the dew point).
"""

from __future__ import annotations

# Hardware channels (reuses the molecular rig's Peltier; cheap, orderable).
HARDWARE = {
    "condenser_peltier": "cools a cold plate below the dew point; water condenses + drips",
    "fan": "moves humid air across the cold plate",
    "carbon_filter": "activated carbon (taste/VOC) — passive inline",
    "uv_led": "UV-C LED sterilises the collected water",
    "dispense_pump": "peristaltic pump to the cup",
    "temp_plate": "Peltier plate to set serving temperature",
}

# base -> (serving temperature C, default volume mL)
PRESETS = {
    "ice water":  (2, 250),
    "cold water": (4, 250),
    "water":      (22, 250),
    "room water": (22, 250),
    "warm water": (40, 250),
    "hot water":  (90, 250),
}
DEFAULT = "water"

# treatment is always applied to harvested water before dispensing
UV_SECONDS_PER_100ML = 12     # UV-C dose time
HARVEST_ML_PER_MIN = 25       # realistic small-Peltier condensation rate (humidity-dependent)
