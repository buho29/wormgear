# Otros generadores de sinfín y rueda

Qué hacen los generadores de sinfín y rueda más conocidos de Fusion 360, FreeCAD, Onshape, Inventor y OpenSCAD, junto a WormGear (v1.1). Sirve para elegir el que mejor encaje con lo que necesitas.

Los datos de los demás salen de su documentación o de su código, revisados el 31/10/2026; no los he ejecutado y pueden haber cambiado. "–" quiere decir que su documentación no lo menciona.

## Tabla

| | WormGear | [GearWorkBench](https://github.com/iplayfast/GearWorkBench) | [freecad.gears](https://github.com/looooo/freecad.gears) | [Helical Gear+](https://github.com/phossystems/HelicalGearPlus) | [Worm Gear FS](https://forum.onshape.com/discussion/31942/custom-feature-worm-gear) | [Inventor](https://help.autodesk.com/cloudhelp/2026/ENU/Inventor-Help/files/GUID-B0203FE2-C1D4-48C1-A062-9F3B43B75F98.htm) | [BOSL2](https://github.com/BelfrySCAD/BOSL2/wiki/gears.scad) |
|---|---|---|---|---|---|---|---|
| CAD | Fusion 360 y FreeCAD | FreeCAD | FreeCAD | Fusion 360 | Onshape | Inventor | OpenSCAD |
| Rueda | Envolvente del sinfín, calculada por planos, con garganta | Diente recto girado con la hélice (como un helicoidal), con garganta | No la hace: solo el sinfín | Helicoidal, no envolvente | Sí; no explica cómo se calcula | Sí, con la curva del diente simplificada | Envolvente, simulando el movimiento de tallado, con abombado |
| Globoide | No | Sí, en un generador aparte | No | No | Sí (v2): rueda plana, doble envolvente plana y Hindley | – | Sinfín globoide sí, con su propia rueda |
| Perfil del sinfín | Flanco recto en la sección axial (ZA), 45° por defecto | Flanco recto en la sección axial, 20° por defecto | Ángulo de presión, 20° por defecto | – | ZA, ZN y ZI | – | Ángulo de presión |
| A izquierdas | Sí | Sí | Sí | – | – | – | Sí |
| Taladros y extremos | Redondo, D, hexagonal, cuadrado, chavetero DIN 6885; tramos lisos | Redondo, cuadrado, hexagonal, chavetero DIN 6885; tramos lisos | – | – | Eje y cubo; fin del filete con salida, chaflán o corte | – | – |
| Comprobación | Interferencia en 8 posiciones y juego medido con los sólidos | Fase de la rueda a mano (`WheelPhase`) | – | – | Interferencia (opción) | Cálculo y comprobación de resistencia | – |
| Rendimiento y autobloqueo | Estimados, con grasa y en seco | – | – | – | Estimados (v2) | – | – |
| Para imprimir | Flanco de 45°, diente bajo y chaflanes, sin soportes | – | – | – | – | – | – |

## Notas

- **GearWorkBench** tiene el mismo tipo de sinfín, con flanco recto en la sección axial. Su rueda es un engranaje helicoidal con garganta, no la envolvente: en el plano medio engrana bien y, lejos de él, los flancos no siguen exactamente al sinfín. Hace también muchos otros tipos de engranaje. Licencia LGPL-2.1.
- **freecad.gears** (FCGear) es el módulo de engranajes más usado de FreeCAD. De este par solo hace el sinfín.
- **Helical Gear+** está gratis en la Autodesk App Store. Su descripción dice que hace sinfines y ruedas "no envolventes": la rueda es un helicoidal normal y el contacto con el sinfín es casi puntual. Para cargas pequeñas suele bastar.
- **Worm Gear FS** (FeatureScript de Onshape, de Younseo Lee) es reciente: la v1 y la v2 se publicaron en el foro de Onshape en octubre. La v2 añade los sinfines globoides y estima el rendimiento y si la rueda puede mover el sinfín. También hace un doble sinfín, con dos sinfines en lados opuestos de la rueda.
- **Inventor** (Design Accelerator) es el único con cálculo de resistencia. Su ayuda dice que la curva del diente se simplifica.
- **BOSL2** genera la rueda envolvente simulando el movimiento de tallado, con abombado para no cargar los bordes. Su documentación avisa de que, lejos del plano medio, los dientes acaban en punta y la holgura no es uniforme en todo el ancho. En 2024, en la lista de correo de OpenSCAD, se dijo que sus sinfines estaban rotos; la documentación de ahora describe el cálculo nuevo.

## Lo que WormGear no hace

- Sinfines globoides (Onshape, GearWorkBench).
- Flancos ZN o ZI (Onshape).
- Doble sinfín (Onshape).
- Cálculo de resistencia (Inventor).

## Rendimiento con flanco de 45°

WormGear usa 45° de flanco por defecto, para imprimir el sinfín de pie sin soportes. Eso tiene un precio: con más ángulo de presión, el rozamiento pesa más y el rendimiento baja. Con el juego por defecto (1 entrada, hélice de 5.4°) y μ = 0.05, sale un 57 % con 45° frente a un 63 % con 20°. Además, la fuerza radial, que separa el sinfín de la rueda, es unas 2.7 veces mayor (tan 45° frente a tan 20°).

A cambio, se autobloquea con más hélice. La rueda no puede mover el sinfín si tan λ ≤ μ / cos αn, con αn el ángulo de presión normal. Con μ = 0.1, eso llega hasta unos 8° de hélice con 45° de flanco, y hasta unos 6° con 20°.

El resumen de WormGear da el rendimiento con grasa (μ 0.1) y en seco (μ 0.3), y dice si se autobloquea. Son estimaciones, porque el rozamiento del plástico impreso varía mucho. Con vibraciones, un sinfín autobloqueante puede volver atrás.

## Fuentes

- [GearWorkBench](https://github.com/iplayfast/GearWorkBench): código de `wormGear.py` y `globoidWormGear.py`.
- [freecad.gears](https://github.com/looooo/freecad.gears): código de `freecad/gears/wormgear.py`.
- [Helical Gear+](https://github.com/phossystems/HelicalGearPlus) y la [Autodesk App Store](https://apps.autodesk.com/FUSION/en/Home).
- [Worm Gear FS v1](https://forum.onshape.com/discussion/31942/custom-feature-worm-gear) y [v2.0](https://forum.onshape.com/discussion/31969/custom-feature-worm-gear-v2-0-now-supporting-globoid-worm-gears), en el foro de Onshape.
- [Inventor: generador de sinfín](https://help.autodesk.com/cloudhelp/2026/ENU/Inventor-Help/files/GUID-B0203FE2-C1D4-48C1-A062-9F3B43B75F98.htm), en la ayuda de Autodesk.
- [BOSL2: `gears.scad`](https://github.com/BelfrySCAD/BOSL2/wiki/gears.scad) y el [hilo de 2024](https://lists.openscad.org/empathy/thread/SDRX76E576Y5ER3LS4HURCNH5N2QUDSW) de la lista de OpenSCAD.
