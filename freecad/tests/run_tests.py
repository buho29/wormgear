# Pruebas sin interfaz:  "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" freecad\tests\run_tests.py
# Genera el sinfín y la rueda con tres juegos de parámetros y comprueba que:
# - los dos sólidos son válidos y la rueda sale con unas 6 caras por diente;
# - no hay interferencia en 8 fases de un diente y el juego medido es la holgura pedida;
# - geometry.py es idéntico al del add-in de Fusion.
# Si existe la variable WORMGEAR_OUT, deja ahí el STL de cada pieza.
import filecmp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import freecad  # noqa: E402
if os.path.join(ROOT, 'freecad') not in freecad.__path__:
    freecad.__path__.append(os.path.join(ROOT, 'freecad'))

import MeshPart  # noqa: E402
from freecad.wormgear import geometry as G, shapes as S, check as C  # noqa: E402

CASES = [
    ('por defecto', {}),
    ('m2 2 entradas 30°', dict(module=2, teeth=20, starts=2, flank_deg=30, addendum_f=0.8, dedendum_f=1.0,
                              worm_pitch_d=20, wheel_width=12, worm_length=36, rim_over_tip=0.8)),
    ('m1.5 60 dientes 3 entradas 30°', dict(module=1.5, teeth=60, starts=3, flank_deg=30, worm_pitch_d=25,
                                            worm_length=40, wheel_width=14)),
]


def main():
    failures = []
    fusion_geometry = os.path.join(ROOT, '..', 'fusion', 'wormgear', 'geometry.py')
    if os.path.exists(fusion_geometry) and not filecmp.cmp(fusion_geometry, os.path.join(ROOT, 'freecad', 'wormgear', 'geometry.py'), False):
        failures.append('geometry.py no es igual que el del add-in de Fusion: cópialo.')
    out = os.environ.get('WORMGEAR_OUT')
    for i, (name, prm) in enumerate(CASES, 1):
        t = time.time()
        q, errors, warns, _ = G.check_params(prm)
        if errors:
            failures.append('%s: %s' % (name, errors))
            continue
        worm = S.worm_shape(q)
        wheel = S.wheel_shape(q)
        t_build = time.time() - t
        res = C.check(q, worm, wheel)
        ok, text = C.report(res, q)
        per_tooth = len(wheel.Faces) / q['teeth']
        print('== %s (%.0f s generar, %.0f s comprobar)' % (name, t_build, time.time() - t - t_build))
        print('   sinfín %d caras %.0f mm³ · rueda %d caras (%.1f por diente) %.0f mm³'
              % (len(worm.Faces), worm.Volume, len(wheel.Faces), per_tooth, wheel.Volume))
        print('   ' + text.replace('\n', '\n   '))
        if not (worm.isValid() and wheel.isValid()):
            failures.append('%s: sólido no válido' % name)
        if not ok:
            failures.append('%s: interferencia' % name)
        if res['play_mm'] is None or abs(res['play_mm'] - q['backlash']) > 0.01:
            failures.append('%s: juego %s mm (pedido %.3f)' % (name, res['play_mm'], q['backlash']))
        if per_tooth > 8:
            failures.append('%s: %.1f caras por diente' % (name, per_tooth))
        if out:
            for label, shape in (('sinfin', worm), ('rueda', wheel)):
                mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.1)
                mesh.write(os.path.join(out, 'caso%d-%s.stl' % (i, label)))
    print('\nFALLOS:\n  ' + '\n  '.join(failures) if failures else '\nTodo bien.')
    return not failures


ok = main()
sys.stdout.flush()
if not ok:
    sys.exit(1)
