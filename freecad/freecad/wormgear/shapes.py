# Sólidos del sinfín y de su rueda lisa con Part (OCCT), sin interfaz: se puede usar desde FreeCADCmd.
# Mismo marco que el add-in de Fusion (ver geometry.py): rueda en el eje Z con centro en el origen,
# sinfín con el eje paralelo a X por (0, A, 0).
# - Sinfín: sección transversal (núcleo + filetes de flanco recto en la sección axial, que en la transversal
#   son espirales de Arquímedes) extruida en hélice, y recortada con un sólido de revolución que lleva los
#   chaflanes de 45° de las puntas y el taladro.
# - Rueda: disco en bruto con garganta, un perfil del hueco por sección (geometry.gap_profile), solevación,
#   patrón circular y corte.
import math

import FreeCAD as App
import Part

from . import geometry as G

V = App.Vector
CHAMFER_BELOW_ROOT = 0.3   # mm


def _bspline(pts):
    c = Part.BSplineCurve()
    c.interpolate(pts)
    return c.toShape()


def _revolve_z(pts):
    """Sólido de revolución alrededor de Z de un polígono cerrado dado como [(r, z)] en el plano XZ."""
    poly = Part.makePolygon([V(r, 0, z) for r, z in pts] + [V(pts[0][0], 0, pts[0][1])])
    return Part.Face(poly).revolve(V(0, 0, 0), V(0, 0, 1), 360)


# ---------------------------------------------------------------- sinfín

def _worm_section(q, x0, n=16):
    """Cara de la sección del sinfín en el plano x = x0, en el marco local del sinfín (eje Z, ángulo t desde +X).
    En la sección axial el filete j ocupa |x - lead·(t - π - 2πj/s)/2π| ≤ hw(r); en x = x0 eso es el sector
    t_c ± 2π·hw(r)/lead, con t_c = π + 2πj/s + 2π·x0/lead."""
    lead, s = q['lead'], q['starts']
    r0, r1 = q['r_root'], q['r_tip']

    def pt(r, t):
        return V(r * math.cos(t), r * math.sin(t), 0)

    def d(r):
        return 2 * math.pi * G.hw(q, r) / lead

    edges = []
    for j in range(s):
        tc = math.pi + 2 * math.pi * j / s + 2 * math.pi * x0 / lead
        nxt = tc + 2 * math.pi / s
        rs = [r0 + (r1 - r0) * i / n for i in range(n + 1)]
        edges.append(_bspline([pt(r, tc - d(r)) for r in rs]))                    # flanco de entrada, fondo -> cresta
        edges.append(Part.Arc(pt(r1, tc - d(r1)), pt(r1, tc), pt(r1, tc + d(r1))).toShape())
        edges.append(_bspline([pt(r, tc + d(r)) for r in reversed(rs)]))          # flanco de salida, cresta -> fondo
        a, b = tc + d(r0), nxt - d(r0)
        edges.append(Part.Arc(pt(r0, a), pt(r0, (a + b) / 2), pt(r0, b)).toShape())
    return Part.Face(Part.Wire(edges))


def _helical_extrusion(face, height, lead):
    """Extruye la cara (plano z = 0) hasta z = height girándola a la vez alrededor de +Z (hélice a derechas).
    Barrido con la binormal fija en Z: las secciones se quedan horizontales y solo giran.
    Con los valores por defecto de OCCT las caras salen de grado 10 y los booleanos contra conos fallan sin avisar
    (el común devuelve el otro sólido entero): con grado ≤ 5 y más tramos salen de grado 4 y cortan bien."""
    spine = Part.makeHelix(lead, height, 10.0, 0, False)
    shell = []
    for wire in face.Wires:
        ps = Part.BRepOffsetAPI.MakePipeShell(spine)
        ps.setBiNormalMode(V(0, 0, 1))
        ps.setMaxDegree(5)
        ps.setMaxSegments(max(400, int(60 * height / lead)))
        ps.add(wire, False, False)
        ps.build()
        shell.extend(ps.shape().Faces)
    top = face.copy()
    top.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(2 * math.pi * height / lead))
    top.translate(V(0, 0, height))
    solid = Part.Solid(Part.Shell(shell + [face, top]))
    if solid.Volume < 0:
        solid.reverse()
    return solid


def _worm_to_world(q):
    """Marco local del sinfín (eje Z, ángulo desde +X hacia +Y) al del mundo (eje X por (0, A, 0), ángulo desde
    +Y hacia +Z): permutación cíclica de los ejes, que es un giro."""
    return App.Matrix(0, 0, 1, 0,
                      1, 0, 0, q['A'],
                      0, 1, 0, 0)


def worm_shape(q):
    L = q['worm_length'] / 2
    lead = q['lead']
    margin = 1.0   # el filete sobra por los extremos y lo recorta el sólido de revolución
    thread = _helical_extrusion(_worm_section(q, -L - margin), 2 * (L + margin), lead)
    thread.translate(V(0, 0, -L - margin))
    # recorte: hasta la cresta (con margen), chaflán de 45° en las puntas y el taladro.
    # El chaflán empieza un poco por debajo del fondo del filete: si el cono pasa justo por la arista del núcleo
    # en la cara del extremo, OCCT falla a menudo el booleano.
    rb = q['worm_bore'] / 2 if q['worm_bore'] > 0 else 0.0
    top = q['r_tip'] + 0.5
    r0 = q['r_root'] - CHAMFER_BELOW_ROOT
    ch = top - r0
    keep = _revolve_z([(rb, -L), (r0, -L), (top, -L + ch), (top, L - ch), (r0, L), (rb, L)])
    worm = _single_solid(thread.common(keep), 'El sinfín')
    # los booleanos de OCCT a veces fallan sin avisar y devuelven uno de los dos sólidos: se mira el volumen
    v_min = math.pi * (r0 ** 2 - rb ** 2) * 2 * L
    v_max = math.pi * (q['r_tip'] ** 2 - rb ** 2) * 2 * L
    if not v_min < worm.Volume < v_max:
        raise RuntimeError('El sinfín ha salido mal (volumen %.0f mm³, tendría que estar entre %.0f y %.0f): '
                           'prueba a cambiar un poco la longitud.' % (worm.Volume, v_min, v_max))
    worm.transformShape(_worm_to_world(q), True)   # con copia: la geometría queda en el mundo, sin Placement
    return worm


# ---------------------------------------------------------------- rueda

def _wheel_blank(q):
    W = q['wheel_width'] / 2
    blank = Part.makeCylinder(q['rim'], 2 * W, V(0, 0, -W))
    blank = blank.cut(Part.makeTorus(q['A'], q['throat']))
    # chaflán de 45° en las caras (doble cono que solo corta fuera de ±chamfer_z) y taladro, en un solo sólido
    rb = q['wheel_bore'] / 2 if q['wheel_bore'] > 0 else 0.0
    W1 = W + 1
    if q['chamfer_z'] is not None:
        zc, rc = q['chamfer_z'], q['chamfer_r']
        keep = _revolve_z([(rb, -W1), (rc - (W1 - zc), -W1), (rc + zc, 0), (rc - (W1 - zc), W1), (rb, W1)])
    else:
        big = q['rim'] + 5
        keep = _revolve_z([(rb, -W1), (big, -W1), (big, W1), (rb, W1)])
    return blank.common(keep)


def _gap_wire(q, c):
    """Perfil cerrado del hueco de un diente en el plano z = c (centrado en +Y), como en el add-in de Fusion:
    flanco izquierdo, arco exterior, flanco derecho y arco de fondo."""
    left, right, rr, ro = G.gap_profile(q, c)
    lp = [V(x, y, c) for x, y in left]
    rp = [V(x, y, c) for x, y in reversed(right)]
    a_out = (G.angle_from_y(left[-1]) + G.angle_from_y(right[-1])) / 2
    a_root = (G.angle_from_y(left[0]) + G.angle_from_y(right[0])) / 2
    return Part.Wire([
        _bspline(lp),
        Part.Arc(lp[-1], V(ro * math.sin(a_out), ro * math.cos(a_out), c), rp[0]).toShape(),
        _bspline(rp),
        Part.Arc(rp[-1], V(rr * math.sin(a_root), rr * math.cos(a_root), c), lp[0]).toShape(),
    ])


def gap_solid(q):
    wires = [_gap_wire(q, c) for c in q['section_z']]
    gap = Part.makeLoft(wires, True, False, False, 5)
    if not gap.isValid() or gap.Volume <= 0:
        raise RuntimeError('La solevación del hueco del diente no ha salido válida.')
    return gap


def wheel_shape(q):
    blank = _wheel_blank(q)
    gap = gap_solid(q)
    gaps = []
    for k in range(q['teeth']):
        g = gap.copy()
        g.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 * k / q['teeth'])
        gaps.append(g)
    wheel = _single_solid(blank.cut(Part.makeCompound(gaps)), 'La rueda')
    if len(wheel.Faces) < 3 * q['teeth'] or wheel.Volume > 0.999 * blank.Volume:
        raise RuntimeError('No se han tallado bien los dientes de la rueda (%d caras): prueba a cambiar un poco '
                           'el ancho o el número de perfiles.' % len(wheel.Faces))
    return wheel


def _single_solid(shape, name):
    """Un único sólido válido (los booleanos de OCCT devuelven un compound)."""
    solids = shape.Solids
    if len(solids) != 1:
        raise RuntimeError('%s ha salido en %d sólidos.' % (name, len(solids)))
    s = solids[0]
    if not s.isValid():
        s.fix(1e-7, 1e-7, 1e-7)
        if not s.isValid():
            raise RuntimeError('%s no es un sólido válido.' % name)
    return s
