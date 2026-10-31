# Other worm gear generators

[Español](comparativa.md) · **English**

What the best-known worm and wheel generators for Fusion 360, FreeCAD, Onshape, Inventor and OpenSCAD do, next to WormGear (v1.2). It is meant to help you pick the one that best fits what you need.

The data on the others comes from their documentation or their code, reviewed on 31/10/2026; I have not run them, and they may have changed. "–" means their documentation does not mention it.

## Table

| | WormGear | [GearWorkBench](https://github.com/iplayfast/GearWorkBench) | [freecad.gears](https://github.com/looooo/freecad.gears) | [Helical Gear+](https://github.com/phossystems/HelicalGearPlus) | [Worm Gear FS](https://forum.onshape.com/discussion/31942/custom-feature-worm-gear) | [Inventor](https://help.autodesk.com/cloudhelp/2026/ENU/Inventor-Help/files/GUID-B0203FE2-C1D4-48C1-A062-9F3B43B75F98.htm) | [BOSL2](https://github.com/BelfrySCAD/BOSL2/wiki/gears.scad) |
|---|---|---|---|---|---|---|---|
| CAD | Fusion 360 and FreeCAD | FreeCAD | FreeCAD | Fusion 360 | Onshape | Inventor | OpenSCAD |
| Wheel | Envelope of the worm, computed per plane, with throat | Straight tooth twisted with the helix (like a helical gear), with throat | Not made: worm only | Helical, non-enveloping | Yes; does not explain how it is computed | Yes, with a simplified tooth curve | Enveloping, simulating the hobbing motion, with crowning |
| Globoid | No | Yes, in a separate generator | No | No | Yes (v2): planar wheel, planar double-enveloping and Hindley | – | Globoid worm yes, with its own wheel |
| Worm profile | Straight flank in the axial section (ZA), 45° by default | Straight flank in the axial section, 20° by default | Pressure angle, 20° by default | – | ZA, ZN and ZI | – | Pressure angle |
| Left-handed | Yes | Yes | Yes | – | – | – | Yes |
| Bores and ends | Round, D, hexagonal, square, DIN 6885 keyway; plain ends | Round, square, hexagonal, DIN 6885 keyway; plain ends | – | – | Shaft and hub; thread end with runout, chamfer or cut | – | – |
| Check | Interference at 8 positions and backlash measured with the solids | Wheel phase set by hand (`WheelPhase`) | – | – | Interference (option) | Strength calculation and check | – |
| Efficiency and self-locking | Estimated, greased and dry | – | – | – | Estimated (v2) | – | – |
| For printing | 45° flank, stub tooth and chamfers, no supports | – | – | – | – | – | – |

## Notes

- **GearWorkBench** has the same kind of worm, with a straight flank in the axial section. Its wheel is a helical gear with a throat, not the envelope: it meshes well in the mid-plane and, away from it, the flanks do not follow the worm exactly. It also makes many other kinds of gears. LGPL-2.1 license.
- **freecad.gears** (FCGear) is the most used gear module in FreeCAD. Of this pair, it only makes the worm.
- **Helical Gear+** is free on the Autodesk App Store. Its description says it makes "non-enveloping" worms and wheels: the wheel is a plain helical gear and the contact with the worm is almost a point. For light loads that is often enough.
- **Worm Gear FS** (an Onshape FeatureScript by Younseo Lee) is recent: v1 and v2 were posted on the Onshape forum in October. v2 adds globoid worms and estimates the efficiency and whether the wheel can drive the worm. It also makes a double worm, with two worms on opposite sides of the wheel.
- **Inventor** (Design Accelerator) is the only one with a strength calculation. Its help says the tooth curve is simplified.
- **BOSL2** generates the enveloping wheel by simulating the hobbing motion, with crowning so the edges are not loaded. Its documentation warns that, away from the mid-plane, the teeth come to a point and the clearance is not uniform across the width. In 2024, on the OpenSCAD mailing list, its worm gears were said to be broken; the current documentation describes the new calculation.

## What WormGear does not do

- Globoid worms (Onshape, GearWorkBench).
- ZN or ZI flanks (Onshape).
- Double worm (Onshape).
- Strength calculation (Inventor).

## Efficiency with a 45° flank

WormGear uses a 45° flank by default, to print the worm standing without supports. That has a price: with a larger pressure angle, friction weighs more and the efficiency drops. With the default set (1 start, 5.4° lead angle) and μ = 0.05, it gives 57 % with 45° versus 63 % with 20°. The radial force, which pushes the worm away from the wheel, is also about 2.7 times larger (tan 45° versus tan 20°).

In return, it self-locks up to a larger lead angle. The wheel cannot drive the worm if tan λ ≤ μ / cos αn, with αn the normal pressure angle. With μ = 0.1, that reaches a lead angle of about 8° with a 45° flank, and about 6° with 20°.

The WormGear summary gives the efficiency greased (μ 0.1) and dry (μ 0.3), and says whether it self-locks. These are estimates, because the friction of printed plastic varies a lot. With vibration, a self-locking worm can back-drive.

## Sources

- [GearWorkBench](https://github.com/iplayfast/GearWorkBench): code of `wormGear.py` and `globoidWormGear.py`.
- [freecad.gears](https://github.com/looooo/freecad.gears): code of `freecad/gears/wormgear.py`.
- [Helical Gear+](https://github.com/phossystems/HelicalGearPlus) and the [Autodesk App Store](https://apps.autodesk.com/FUSION/en/Home).
- [Worm Gear FS v1](https://forum.onshape.com/discussion/31942/custom-feature-worm-gear) and [v2.0](https://forum.onshape.com/discussion/31969/custom-feature-worm-gear-v2-0-now-supporting-globoid-worm-gears), on the Onshape forum.
- [Inventor: worm gear generator](https://help.autodesk.com/cloudhelp/2026/ENU/Inventor-Help/files/GUID-B0203FE2-C1D4-48C1-A062-9F3B43B75F98.htm), in the Autodesk help.
- [BOSL2: `gears.scad`](https://github.com/BelfrySCAD/BOSL2/wiki/gears.scad) and the [2024 thread](https://lists.openscad.org/empathy/thread/SDRX76E576Y5ER3LS4HURCNH5N2QUDSW) on the OpenSCAD list.
