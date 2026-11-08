# Demo de WormGear: rueda de pie y sinfín tumbado encima, cada uno de una sola pieza con sus ejes.
# Los ejes giran en "rodamientos" de dos conos de 45°: medio alojamiento en una columna de la base y la otra
# mitad en una tapa que entra en la columna de arriba abajo, guiada.
# El sinfín lleva un pomo moleteado en un eje.
#
# Salvo el sinfín y la rueda (que salen de wormgear.build), todo se modela con operaciones en la línea de tiempo
# (bocetos, extrusiones, revoluciones, redondeos y patrones), así que se puede editar después en Fusion.
#
# Script de Fusion (UTILIDADES > Scripts): crea el conjunto en el diseño activo, que tiene que estar vacío o
# tener solo una demo anterior (se borra y se vuelve a hacer). Necesita el add-in WormGear en ../../../fusion.
#
# Marco del mundo: Z arriba, la cara de abajo de la base en z = 0.
#   - rueda: eje paralelo a Y, centro en (0, 0, H);
#   - sinfín: eje paralelo a X, por (0, 0, H + A), encima de la rueda.
# El sinfín y la rueda se generan con wormgear.build en su marco propio (rueda en Z, sinfín en X por y = A)
# y se colocan con la matriz WG: X -> X, Y -> Z, Z -> -Y. Sus ejes se modelan en ese marco propio.
import importlib
import math
import os
import sys
import traceback

import adsk.core
import adsk.fusion

HERE = os.path.dirname(os.path.abspath(__file__))
FUSION_DIR = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'fusion'))
if FUSION_DIR not in sys.path:
    sys.path.insert(0, FUSION_DIR)
import wormgear.geometry  # noqa: E402
import wormgear.build  # noqa: E402
import wormgear.check  # noqa: E402
from wormgear import geometry as G, build as B, check as C  # noqa: E402

MM = 0.1   # Fusion trabaja en cm
ATTR = 'WormGearDemo'   # grupo de atributos que marca lo que crea la demo

# ---------------------------------------------------------------- medidas (mm)
# engrane por defecto de WormGear con flanco de 45°, sin taladros (los ejes son de la misma pieza)
GEAR = dict(flank_deg=45.0, worm_length=35.0, worm_bore=0.0, wheel_bore=0.0)   # sinfín 5 mm más largo que el de serie (30)
FIT = 0.1          # holgura por lado entre piezas impresas
WALL = 3.2         # pared mínima
H = 40.0           # altura del eje de la rueda (la rueda queda a 4 mm de la placa)
PLATE_T = 12.0     # grosor de la placa
# eje: cuello de NECK_D y "rodamiento" de dos conos de 45° (de NECK_D a BRG_SHAFT_D y vuelta a NECK_D) separados por
# un cilindro de BRG_GAP. Los ejes no llevan caras planas: todos los cambios de Ø son conos de 45°.
NECK_D = 6.0
BRG_D = 10.0
BRG_GAP = 1.0
BRG_SHAFT_D = 9.9  # Ø del cilindro del rodamiento en el eje: 0.1 menos que BRG_D (el hueco sigue en BRG_D + 2·FIT);
                   # los conos siguen a 45° y el cilindro se alarga lo que acortan
TIP_L = 3.0        # punta que asoma por fuera del alojamiento: el cuello recto, con un chaflán de 0.5
CHANNEL = 3.5      # tramo de cuello dentro del alojamiento, a cada lado de los conos (columna de 12 de grueso)
HUB_D = 16.0       # base del cono de 45° que sale de la cara de la rueda
GAP = 0.5          # entre una pieza que gira y la cara de la columna
TOWER_GAP_X = 1.6  # entre el borde de la rueda y las columnas del sinfín
# rebaje de la cara de abajo de la rueda (la que va a la cama): el contorno de la cara, con los dientes, desfasado
# DISH_RING hacia dentro (ahí apoya el soporte de impresión), y una solevación hasta el mismo contorno DISH_DEPTH
# más adentro y DISH_DEPTH más hondo: la pared sigue los dientes y no baja de 45° (menos puente)
DISH_RING = 0.8
DISH_DEPTH = 7.0
# soporte de la rueda para imprimirla de pie sobre el eje de abajo: el anillo de DISH_RING de la cara de abajo
# extruido hasta la cama, con un ala (brim) en la cama; en sección es una L. Va en su propio cuerpo, sin unir
SUPPORT_BRIM = 6.0    # lo que sale el ala por fuera del borde de la rueda
SUPPORT_BRIM_T = 0.6  # grueso del ala
# columna: horquilla abierta arriba; la tapa entra de arriba abajo entre los dos brazos, guiada por una lengüeta
# a cada lado en una ranura vertical
TONGUE_D = 1.0     # lo que entra la lengüeta en el brazo
TONGUE_T = 3.0     # ancho de la lengüeta (a lo largo del eje)
CAP_H = 9.5        # alto de la tapa por encima del eje
# redondeo de las aristas de arriba en las caras por las que pasa el eje (columna y tapa a la vez). La ranura de
# la lengüeta está a 4.3 mm de la cara: con 4 solo el último 0.4 mm junto a la ranura baja de 2 mm de pared, y a
# la tapa, que se imprime boca abajo, le queda un plano de (grueso - 2·TOP_R) para apoyar
TOP_R = 4.0
# redondeo del contorno de la cara de fuera de los brazos: con 1, junto a las caras del eje el brazo (3.4) se queda
# en 2.4, y arriba, detrás de la ranura de la lengüeta (2.4), solo el filo de los últimos 0.2 mm baja de 2 mm
ARM_R = 1.0
GROOVE_FROM_BRG = 2.0   # del ecuador del hueco del rodamiento al fondo de la ranura de la lengüeta
CAP_WALL = GROOVE_FROM_BRG - TONGUE_D - FIT   # pared de la tapa a los lados del hueco (la lengüeta la refuerza)
ARM_WALL = 2.4     # pared de los brazos detrás de la ranura de la lengüeta
# pomo moleteado en el eje izquierdo del sinfín
KNOB_D = 16.0
KNOB_L = 14.0
KNOB_GROOVES = 18
KNOB_GROOVE = 0.8  # profundidad de las estrías
# grabados: en los chaflanes largos de la placa (delante el nombre, detrás la relación y el módulo) y una flecha
# radial en la cara de arriba de la rueda (la de arriba al imprimir), para ver cómo gira
ENGRAVE = 0.6      # profundidad
TEXT_H = 7.0       # alto de las letras
ARROW = dict(r0=10.5, r1=17.0, r2=21.5, shaft=2.4, head=7.0)   # radios de la flecha y anchos (mm)
# chaflán asimétrico alrededor de lo alto de la placa: baja PLATE_CHAMFER_V por el lado y entra PLATE_CHAMFER_H
PLATE_CHAMFER_V = 4.0
PLATE_CHAMFER_H = 14.0
PLATE_MARGIN = 15.0  # de las columnas al borde de la placa (más que lo que entra el chaflán)
PLATE_R = 16.0       # esquinas de la placa (más que lo que entra el chaflán, para que el chaflán las siga)
PLATE_EDGE_R = 4.0   # redondeo entre el lado de la placa y el chaflán (se come unos 3 mm de cada cara)
# colores, como los de la foto: lo que gira en morado, las tapas en turquesa
COLORS = {'Demo morado': (170, 140, 230), 'Demo turquesa': (90, 200, 220), 'Demo blanco': (235, 235, 235)}

BRG_CONE = (BRG_D - NECK_D) / 2                       # largo de cada cono de 45°
BRG_L = 2 * BRG_CONE + BRG_GAP                        # largo del rodamiento
HOUSING_T = BRG_L + 2 * CHANNEL                       # grueso de la columna y de la tapa a lo largo del eje
CAP_W = BRG_D + 2 * FIT + 2 * CAP_WALL                # ancho de la tapa (perpendicular al eje)
ARM = ARM_WALL + TONGUE_D                             # brazos de la horquilla
COL_W = CAP_W + 2 * FIT + 2 * ARM                     # ancho de la columna


# ---------------------------------------------------------------- utilidades
def P(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def V(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def add(a, b):
    return tuple(p + q for p, q in zip(a, b))


def mul(a, k):
    return tuple(p * k for p in a)


def dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def matrix(cols, origin):
    """Matriz con las columnas dadas (imágenes de X, Y, Z) y el origen en mm."""
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(*origin), V(*cols[0]), V(*cols[1]), V(*cols[2]))
    return m


def wg_matrix():
    """Del marco de WormGear al de la demo: el sinfín queda encima de la rueda."""
    return matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)), (0, 0, H))


# ---------------------------------------------------------------- perfiles [(s, r)] a lo largo de un eje
def bearing_profile(s0, sign):
    """Perfil del rodamiento a partir de s0 (cara interior del alojamiento), hacia fuera con signo sign:
    cuello, cono que abre, cilindro, cono que cierra y cuello. Devuelve [(s, r)] y el s de la cara exterior."""
    rn, rb = NECK_D / 2, BRG_SHAFT_D / 2
    dr = (BRG_D - BRG_SHAFT_D) / 2   # lo que se acorta cada cono
    s = [s0]
    for d in (CHANNEL, BRG_CONE, BRG_GAP, BRG_CONE, CHANNEL):
        s.append(s[-1] + sign * d)
    return [(s[0], rn), (s[1], rn), (s[2] - sign * dr, rb), (s[3] + sign * dr, rb), (s[4], rn), (s[5], rn)], s[5]


def shaft_profile(face_s, face_r, housing_s, sign, outer):
    """Eje que sale de una cara de radio face_r en face_s, con un cono de 45° hasta el cuello, el rodamiento
    desde housing_s y, por fuera, outer = [(distancia, r)] (punta o pomo). Devuelve [(s, r)] y el s de la cara
    exterior del alojamiento. Empieza 0.3 mm dentro de la pieza para que se una bien."""
    rn = NECK_D / 2
    hub_end = face_s + sign * (face_r - rn)
    prof = [(face_s - sign * 0.3, face_r), (face_s, face_r), (hub_end, rn)]
    brg, s_out = bearing_profile(housing_s, sign)
    prof += brg + [(s_out + sign * d, r) for d, r in outer]
    return prof, s_out


def tip():
    """Punta: el cuello sigue recto TIP_L y acaba en un chaflán de 0.5."""
    return [(TIP_L - 0.5, NECK_D / 2), (TIP_L, NECK_D / 2 - 0.5)]


def housing_profile():
    """Hueco del rodamiento (el eje + FIT) respecto al centro del alojamiento, alargado por fuera de las caras."""
    rn, rb = NECK_D / 2 + FIT, BRG_D / 2 + FIT
    ht = HOUSING_T / 2
    c = BRG_GAP / 2
    # los conos del hueco van FIT por fuera de los del eje: sus extremos se desplazan FIT·(√2 - 1)
    d = FIT * (math.sqrt(2) - 1)
    return [(-ht - 1, rn), (-(c + BRG_CONE + d), rn), (-(c + d), rb), (c + d, rb), (c + BRG_CONE + d, rn),
            (ht + 1, rn)]


def closed(prof):
    """Perfil [(s, r)] cerrado por el eje (r = 0), para revolucionarlo."""
    return [(prof[0][0], 0.0)] + list(prof) + [(prof[-1][0], 0.0)]


def plus(u_half, v_half, tu_half, tv_half):
    """Contorno en cruz (u, v): rectángulo de 2·u_half × 2·v_half con una lengüeta de 2·tu_half de ancho a cada
    lado en v, hasta ±tv_half (la tapa con sus lengüetas, o el hueco de la tapa con sus ranuras)."""
    a, b, t, g = v_half, u_half, tu_half, tv_half
    return [(-b, -a), (-t, -a), (-t, -g), (t, -g), (t, -a), (b, -a), (b, a), (t, a), (t, g), (-t, g), (-t, a), (-b, a)]


def diamond(hd):
    """Rombo (u, v) de semidiagonal hd, con las puntas arriba y abajo (techo a 45°)."""
    return [(hd, 0), (0, hd), (-hd, 0), (0, -hd)]


class Layout:
    """Posiciones de todo a partir de q."""

    def __init__(self, q):
        self.q = q
        A = q['A']
        self.A = A
        self.Hw = H + A                  # altura del eje del sinfín
        W = q['wheel_width'] / 2
        L = q['worm_length'] / 2
        r_wheel = q['rim']
        # rueda (eje Y): columnas a los dos lados, pasado el cono del cubo
        self.w_face = W
        self.w_hub_end = W + (HUB_D / 2 - NECK_D / 2)
        self.w_housing = self.w_hub_end + GAP            # cara interior de la columna (|y|)
        self.w_bed = self.w_housing + HOUSING_T + TIP_L  # punta del eje de abajo: la cama al imprimir (|z|)
        # rebaje: empieza DISH_RING por dentro del fondo de los dientes en la cara
        self.dish_r = G.gap_profile(q, W)[2] - DISH_RING
        # sinfín (eje X): columnas pasado el borde de la rueda
        r_end = q['r_chamfer']                           # radio del sinfín en sus extremos
        self.s_face = L
        self.s_housing = max(r_wheel + TOWER_GAP_X, L + (r_end - NECK_D / 2) + GAP)
        self.knob_gap = 2.0
        self.label = '%d:%d  m%g' % (q['teeth'], q['starts'], q['module'])
        # base
        reach_x = self.s_housing + HOUSING_T + PLATE_MARGIN
        reach_y = self.w_housing + HOUSING_T + PLATE_MARGIN
        self.plate = (-reach_x, reach_x, -reach_y, reach_y)
        assert H - r_wheel > PLATE_T + 1, 'la rueda toca la base'
        assert self.Hw - q['r_tip'] > H + CAP_H + 1, 'el sinfín toca las tapas de la rueda'
        assert self.s_housing > COL_W / 2 + 1, 'las columnas de la rueda tocan las del sinfín'
        assert self.dish_r - DISH_DEPTH > HUB_D / 2 + 1, 'el rebaje no deja sitio al cono del eje'

    def dish_contour(self, per_tooth=36):
        """Contorno de la cara z = -W desfasado DISH_RING hacia dentro, como [(θ, r)] en un paso de diente
        (θ desde +Y hacia +X, como geometry.angle_from_y). Para cada θ, el mayor r cuyo círculo de DISH_RING
        queda dentro de la cara (fuera del hueco del diente y dentro del borde)."""
        q = self.q
        left, right, rr, _ = G.gap_profile(q, -self.w_face)
        a0, a1 = G.angle_from_y(left[0]), G.angle_from_y(right[0])
        root = [(rr * math.sin(a1 + (a0 - a1) * i / 8), rr * math.cos(a1 + (a0 - a1) * i / 8)) for i in range(9)]
        gap = left + list(reversed(right)) + root     # contorno cerrado del hueco
        segs = [(a, b) for a, b in zip(gap, gap[1:] + gap[:1]) if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-9]

        def dist(x, y):
            d = q['rim'] - math.hypot(x, y)
            for (x0, y0), (x1, y1) in segs:
                dx, dy = x1 - x0, y1 - y0
                t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
                d = min(d, math.hypot(x - x0 - t * dx, y - y0 - t * dy))
            return d

        pitch = 2 * math.pi / q['teeth']
        ac = (a0 + a1) / 2
        out = []
        for i in range(per_tooth):
            th = ac - pitch / 2 + pitch * i / per_tooth
            lo, hi = rr - DISH_RING - 1.0, q['rim'] - DISH_RING
            for _ in range(30):
                mid = (lo + hi) / 2
                if dist(mid * math.sin(th), mid * math.cos(th)) >= DISH_RING:
                    lo = mid
                else:
                    hi = mid
            out.append((th, lo))
        return out

    def wheel_shaft_profiles(self):
        """Los dos ejes de la rueda, a lo largo de su eje Z (marco de WormGear). Por abajo, el cono del cubo
        sale del fondo del rebaje."""
        top, _ = shaft_profile(self.w_face, HUB_D / 2, self.w_housing, 1, tip())
        bottom, _ = shaft_profile(-(self.w_face - DISH_DEPTH), HUB_D / 2, -self.w_housing, -1, tip())
        return [top, bottom]

    def worm_shaft_profiles(self):
        """Los dos ejes del sinfín, a lo largo de su eje X; el de la izquierda sigue hasta el pomo, que empieza
        con un cono de 45°. Devuelve ([perfiles], (x del principio, x del final) del cilindro del pomo)."""
        r_end = self.q['r_chamfer']
        right, _ = shaft_profile(self.s_face, r_end, self.s_housing, 1, tip())
        rn, kr = NECK_D / 2, KNOB_D / 2
        g = self.knob_gap
        k0 = g + (kr - rn)
        knob = [(g, rn), (k0, kr), (k0 + KNOB_L - 0.5, kr), (k0 + KNOB_L, kr - 0.5)]
        left, s_out = shaft_profile(-self.s_face, r_end, -self.s_housing, -1, knob)
        return [right, left], (s_out - k0, s_out - k0 - KNOB_L)

    def housings(self):
        """Los dos grupos de alojamientos, en el marco del mundo: [(eje, altura del eje, [centros])]."""
        ht = HOUSING_T / 2
        return [((0, 1, 0), H, [(0, s * (self.w_housing + ht), H) for s in (1, -1)]),
                ((1, 0, 0), self.Hw, [(s * (self.s_housing + ht), 0, self.Hw) for s in (1, -1)])]


# ---------------------------------------------------------------- operaciones en la línea de tiempo
def _sketch(comp, plane, name):
    sk = comp.sketches.add(plane)
    sk.name = name
    return sk


def _poly(sk, pts):
    """Polígono cerrado por los puntos del modelo pts (mm), con los extremos de las líneas compartidos."""
    sp = []
    for p in pts:
        q_ = sk.modelToSketchSpace(P(*p))
        if not sp or q_.distanceTo(sp[-1]) > 1e-7:
            sp.append(q_)
    if sp[0].distanceTo(sp[-1]) < 1e-7:
        sp.pop()
    lines = sk.sketchCurves.sketchLines
    first = prev = None
    for i in range(len(sp)):
        a = prev.endSketchPoint if prev else sp[0]
        b = first.startSketchPoint if i == len(sp) - 1 else sp[i + 1]
        prev = lines.addByTwoPoints(a, b)
        if first is None:
            first = prev


def _all_profiles(sk):
    oc = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        oc.add(pr)
    return oc


def _plane_at(comp, base_plane, offset, name):
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(base_plane, adsk.core.ValueInput.createByReal(offset * MM))
    pl = comp.constructionPlanes.add(pin)
    pl.name = name
    pl.isLightBulbOn = False
    return pl


def _extrude(comp, profiles, dist, op, name, bodies=None, symmetric=False):
    ei = comp.features.extrudeFeatures.createInput(profiles, op)
    d = adsk.core.ValueInput.createByReal(dist * MM)
    if symmetric:
        ei.setSymmetricExtent(d, True)
    else:
        ei.setDistanceExtent(False, d)
    if bodies:
        ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    return f


def _revolve(comp, plane, polys, axis, op, name, bodies=None):
    """Revoluciona los polígonos polys (puntos del modelo, mm) alrededor de la línea axis = (p0, p1)."""
    sk = _sketch(comp, plane, name)
    for pts in polys:
        _poly(sk, pts)
    ax = sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(P(*axis[0])),
                                                     sk.modelToSketchSpace(P(*axis[1])))
    ax.isConstruction = True
    ri = comp.features.revolveFeatures.createInput(_all_profiles(sk), ax, op)
    ri.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    if bodies:
        ri.participantBodies = bodies
    f = comp.features.revolveFeatures.add(ri)
    f.name = name
    sk.isVisible = False
    return f, ax


def _param(design, name, mm, comment, at_least=None):
    """Parámetro de usuario en mm: se crea con el valor del script si no existe; si ya existe, se respeta el
    que tenga (puede haberlo cambiado el usuario), salvo que sea menor que at_least. Devuelve el nombre, para
    usarlo como expresión."""
    prm = design.userParameters.itemByName(name)
    if prm is None:
        design.userParameters.add(name, adsk.core.ValueInput.createByString('%g mm' % mm), 'mm', comment)
    elif at_least is not None and prm.value / MM < at_least:
        prm.expression = '%g mm' % mm
    return name


def _fillet(comp, edges, r, name):
    """Redondeo de radio r: en mm, o el nombre de un parámetro de usuario."""
    oc = adsk.core.ObjectCollection.create()
    for e in edges:
        oc.add(e)
    fi = comp.features.filletFeatures.createInput()
    rv = adsk.core.ValueInput.createByString(r) if isinstance(r, str) else adsk.core.ValueInput.createByReal(r * MM)
    try:
        fi.edgeSetInputs.addConstantRadiusEdgeSet(oc, rv, False)
    except AttributeError:
        fi.addConstantRadiusEdgeSet(oc, rv, False)
    f = comp.features.filletFeatures.add(fi)
    f.name = name
    return f


def _line_edges(body, test):
    """Aristas rectas del cuerpo cuyos extremos (mm) cumplen test(p0, p1)."""
    out = []
    for e in body.edges:
        g = e.geometry
        if isinstance(g, adsk.core.Line3D):
            p0 = (g.startPoint.x / MM, g.startPoint.y / MM, g.startPoint.z / MM)
            p1 = (g.endPoint.x / MM, g.endPoint.y / MM, g.endPoint.z / MM)
            if test(p0, p1):
                out.append(e)
    return out


def _near(a, b, tol=1e-3):
    return abs(a - b) < tol


def _top_edges(body, axis, center, top):
    """Aristas de arriba (z = top) en las dos caras por las que pasa el eje (a ±HOUSING_T/2 del centro)."""
    ht = HOUSING_T / 2

    def test(p0, p1):
        if not (_near(p0[2], top) and _near(p1[2], top)):
            return False
        # los dos extremos en la misma cara (si no, es una arista a lo largo del eje, de cara a cara)
        a0, a1 = dot(add(p0, mul(center, -1)), axis), dot(add(p1, mul(center, -1)), axis)
        return _near(abs(a0), ht) and _near(a0, a1)
    return _line_edges(body, test)


def _plate_top(body):
    """Cara de arriba de la placa (plana, a z = PLATE_T, la más grande)."""
    best = None
    for f in body.faces:
        g = f.geometry
        if isinstance(g, adsk.core.Plane) and g.normal.z > 0.99 and _near(f.pointOnFace.z / MM, PLATE_T):
            if best is None or f.area > best.area:
                best = f
    return best


def _plate_chamfer(comp, body, lay):
    """Chaflán asimétrico alrededor de lo alto de la placa. Qué distancia va a cada cara depende de cómo vea
    Fusion la arista, así que se comprueba con la cara de arriba y, si sale al revés, se hace volteado."""
    oc = adsk.core.ObjectCollection.create()
    for e in [lp for lp in _plate_top(body).loops if lp.isOuter][0].edges:
        oc.add(e)
    x1 = lay.plate[1]
    feats = comp.features.chamferFeatures
    for flipped in (False, True):
        ci = feats.createInput2()
        ci.chamferEdgeSets.addTwoDistancesChamferEdgeSet(
            oc, adsk.core.ValueInput.createByReal(PLATE_CHAMFER_H * MM),
            adsk.core.ValueInput.createByReal(PLATE_CHAMFER_V * MM), flipped, True)
        try:
            f = feats.add(ci)
        except RuntimeError:
            continue   # al revés no cabe: 14 mm por un lado de 12
        top = _plate_top(comp.bRepBodies.item(0))
        if top is not None and _near(top.boundingBox.maxPoint.x / MM, x1 - PLATE_CHAMFER_H, 0.01):
            f.name = 'Chaflán de la placa'
            return f
        f.deleteMe()
    raise RuntimeError('No ha salido el chaflán de la placa.')


def _outward(face):
    ok, n = face.evaluator.getNormalAtPoint(face.pointOnFace)
    return (n.x, n.y, n.z)


def _cut_into(comp, profile, depth, body, name):
    """Extrusión de corte de depth (mm) hacia dentro del cuerpo desde un boceto en una de sus caras (la normal
    del boceto es la de fuera de la cara)."""
    return _extrude(comp, profile, -depth, adsk.fusion.FeatureOperations.CutFeatureOperation, name, [body])


def _engrave_text(comp, face, text, body, name):
    """Texto grabado ENGRAVE en una cara plana, centrado, leyéndose de izquierda a derecha visto desde fuera y
    con la parte de arriba de las letras hacia arriba (la cara puede estar inclinada)."""
    n = _outward(face)
    right = cross((0, 0, 1), n)
    ln = math.sqrt(dot(right, right))
    right = mul(right, 1 / ln)
    up = cross(n, right)
    c = face.centroid
    c = (c.x / MM, c.y / MM, c.z / MM)
    sk = _sketch(comp, face, name)
    # caja de texto centrada en la cara y girada para que lea en la dirección right
    sx, sy = sk.xDirection, sk.yDirection
    ang = math.atan2(dot(right, (sy.x, sy.y, sy.z)), dot(right, (sx.x, sx.y, sx.z)))
    cs = sk.modelToSketchSpace(P(*c))
    w2, h2 = 60.0 * MM, TEXT_H * MM
    ti = sk.sketchTexts.createInput2(text, TEXT_H * MM)
    ti.setAsMultiLine(adsk.core.Point3D.create(cs.x - w2, cs.y - h2, 0), adsk.core.Point3D.create(cs.x + w2, cs.y + h2, 0),
                      adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                      adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
    ti.angle = ang
    try:
        ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
    except Exception:
        pass
    st = sk.sketchTexts.add(ti)
    sk.isVisible = False
    return _cut_into(comp, st, ENGRAVE, body, name)


def build_base(root, lay):
    """Base: placa con las esquinas redondeadas y cuatro columnas en horquilla, con medio alojamiento, las
    ranuras de las lengüetas de la tapa y el redondeo de arriba."""
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = 'Base'
    _mark(occ, 'base')
    NB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    x0, x1, y0, y1 = lay.plate
    sk = _sketch(comp, comp.xYConstructionPlane, 'Placa')
    _poly(sk, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)])
    sk.isVisible = False
    body = _extrude(comp, sk.profiles.item(0), PLATE_T, NB, 'Placa').bodies.item(0)
    body.name = 'Base'
    _fillet(comp, _line_edges(body, lambda p0, p1: _near(p0[0], p1[0]) and _near(p0[1], p1[1])),
            _param(comp.parentDesign, 'redondeo_placa', PLATE_R, 'Esquinas de la placa de la demo',
                   at_least=PLATE_CHAMFER_H + 0.5),
            'Esquinas de la placa')
    body = comp.bRepBodies.item(0)
    _plate_chamfer(comp, body, lay)
    body = comp.bRepBodies.item(0)
    z = PLATE_T - PLATE_CHAMFER_V   # arista entre el lado de la placa y el chaflán, todo alrededor
    edges = [e for e in body.edges
             if _near(e.boundingBox.minPoint.z / MM, z) and _near(e.boundingBox.maxPoint.z / MM, z)]
    _fillet(comp, edges, _param(comp.parentDesign, 'redondeo_chaflan', PLATE_EDGE_R,
                                'Redondeo entre el lado de la placa de la demo y su chaflán'),
            'Redondeo del chaflán')
    body = comp.bRepBodies.item(0)
    ht = HOUSING_T / 2
    for axis, cz, centers in lay.housings():
        w = cross(axis, (0, 0, 1))   # horizontal, perpendicular al eje
        tag = 'rueda' if axis[1] else 'sinfín'

        def at(c, u, v, z):
            """Punto del centro c, u a lo largo del eje, v a lo largo de w, a la altura z."""
            return add(add(add(c, mul(axis, u)), mul(w, v)), (0, 0, z - c[2]))
        # columnas
        sk = _sketch(comp, comp.xYConstructionPlane, 'Columnas %s' % tag)
        for c in centers:
            _poly(sk, [at(c, u, v, 0) for u, v in ((-ht, -COL_W / 2), (ht, -COL_W / 2), (ht, COL_W / 2), (-ht, COL_W / 2))])
        sk.isVisible = False
        _extrude(comp, _all_profiles(sk), cz + CAP_H, JOIN, 'Columnas %s' % tag, [body])
        # hueco de la tapa con las ranuras de las lengüetas, desde el eje hacia arriba
        pl = _plane_at(comp, comp.xYConstructionPlane, cz, 'Eje %s' % tag)
        sk = _sketch(comp, pl, 'Hueco de las tapas %s' % tag)
        for c in centers:
            _poly(sk, [at(c, u, v, cz) for u, v in plus(ht + 1, CAP_W / 2 + FIT, TONGUE_T / 2 + FIT,
                                                         CAP_W / 2 + TONGUE_D + FIT)])
        sk.isVisible = False
        _extrude(comp, _all_profiles(sk), CAP_H + 1, CUT, 'Hueco de las tapas %s' % tag, [body])
        # medio alojamiento: revolución del hueco del rodamiento alrededor del eje
        plane = comp.yZConstructionPlane if axis[1] else comp.xZConstructionPlane
        polys = [[at(c, s, 0, cz + r) for s, r in closed(housing_profile())] for c in centers]
        line = (at(centers[0], -200, 0, cz), at(centers[0], 200, 0, cz))
        _revolve(comp, plane, polys, line, CUT, 'Alojamientos %s' % tag, [body])
        # redondeo de arriba en las caras por las que pasa el eje
        body = comp.bRepBodies.item(0)
        edges = []
        for c in centers:
            edges += _top_edges(body, axis, c, cz + CAP_H)
        _fillet(comp, edges, _param(comp.parentDesign, 'redondeo_columnas', TOP_R,
                                    'Redondeo de arriba de las columnas y las tapas de la demo'),
                'Redondeo columnas %s' % tag)
        body = comp.bRepBodies.item(0)
        # contorno de la cara de fuera de cada brazo (menos la arista del pie, junto a la placa)
        edges = []
        for f in body.faces:
            g = f.geometry
            if not isinstance(g, adsk.core.Plane) or abs(abs(dot((g.normal.x, g.normal.y, g.normal.z), w)) - 1) > 1e-6:
                continue
            p = f.pointOnFace
            p = (p.x / MM, p.y / MM, p.z / MM)
            if not any(_near(abs(dot(add(p, mul(c, -1)), w)), COL_W / 2) and
                       abs(dot(add(p, mul(c, -1)), axis)) < HOUSING_T / 2 for c in centers):
                continue
            for e in [lp for lp in f.loops if lp.isOuter][0].edges:
                bb = e.boundingBox
                if not (_near(bb.minPoint.z / MM, PLATE_T) and _near(bb.maxPoint.z / MM, PLATE_T)):
                    edges.append(e)
        _fillet(comp, edges, _param(comp.parentDesign, 'redondeo_brazos', ARM_R,
                                    'Redondeo de la cara de fuera de los brazos de las columnas de la demo'),
                'Redondeo brazos %s' % tag)
        body = comp.bRepBodies.item(0)
    # grabados en los dos chaflanes largos de la placa (los que miran a -Y y a +Y)
    for sign, text in ((-1, 'WormGear'), (1, lay.label)):
        best = None
        for f in body.faces:
            if isinstance(f.geometry, adsk.core.Plane):
                n = _outward(f)
                if n[2] > 0.5 and n[1] * sign > 0.2 and (best is None or f.area > best.area):
                    best = f
        _engrave_text(comp, best, text, body, 'Grabado %s' % text)
        body = comp.bRepBodies.item(0)
    return occ


def build_caps(root, lay):
    """Tapa (un componente, cuatro ocurrencias): en su marco, el eje va a lo largo de X por el origen."""
    NB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    places = []
    for axis, cz, centers in lay.housings():
        cols = ((1, 0, 0), (0, 1, 0), (0, 0, 1)) if axis[0] else ((0, 1, 0), (-1, 0, 0), (0, 0, 1))
        places += [matrix(cols, c) for c in centers]
    occ = root.occurrences.addNewComponent(places[0])
    comp = occ.component
    comp.name = 'Tapa'
    ht = HOUSING_T / 2
    sk = _sketch(comp, comp.xYConstructionPlane, 'Tapa')
    _poly(sk, [(u, v, 0) for u, v in plus(ht, CAP_W / 2, TONGUE_T / 2, CAP_W / 2 + TONGUE_D)])
    sk.isVisible = False
    body = _extrude(comp, sk.profiles.item(0), CAP_H, NB, 'Tapa').bodies.item(0)
    body.name = 'Tapa'
    _revolve(comp, comp.xZConstructionPlane, [[(s, 0, r) for s, r in closed(housing_profile())]],
             ((-200, 0, 0), (200, 0, 0)), CUT, 'Alojamiento', [body])
    body = comp.bRepBodies.item(0)
    _fillet(comp, _top_edges(body, (1, 0, 0), (0, 0, 0), CAP_H),
            _param(comp.parentDesign, 'redondeo_columnas', TOP_R, ''), 'Redondeo')
    occs = [occ] + [root.occurrences.addExistingComponent(comp, m) for m in places[1:]]
    for o in occs:
        _mark(o, 'cap')
    return occs


def add_wheel_arrow(comp, body, lay):
    """Flecha radial grabada en la cara de arriba de la rueda (z = +W en su marco, la que no lleva rebaje)."""
    W = lay.w_face
    face = None
    for f in body.faces:
        if isinstance(f.geometry, adsk.core.Plane) and _outward(f)[2] > 0.99 and _near(f.pointOnFace.z / MM, W):
            if face is None or f.area > face.area:
                face = f
    a = ARROW
    pts = [(-a['shaft'] / 2, a['r0']), (a['shaft'] / 2, a['r0']), (a['shaft'] / 2, a['r1']), (a['head'] / 2, a['r1']),
           (0, a['r2']), (-a['head'] / 2, a['r1']), (-a['shaft'] / 2, a['r1'])]
    sk = _sketch(comp, face, 'Flecha')
    _poly(sk, [(x, y, W) for x, y in pts])
    sk.isVisible = False
    # el boceto en la cara también trae sus aristas proyectadas: la flecha es el perfil más pequeño
    prof = min(sk.profiles, key=lambda pr: pr.areaProperties().area)
    _cut_into(comp, prof, ENGRAVE, body, 'Flecha')
    return comp.bRepBodies.item(0)


def add_wheel_support(comp, body, lay):
    """Soporte para imprimir la rueda de pie sobre su eje de abajo: la cara z = -W (el anillo que deja el rebaje)
    extruida hasta la cama, más un ala en la cama hasta SUPPORT_BRIM por fuera del borde de la rueda. Es otro
    cuerpo del componente de la rueda, sin unir, y queda oculto en el montaje (atraviesa las columnas)."""
    W = lay.w_face
    face = None
    for f in body.faces:
        if isinstance(f.geometry, adsk.core.Plane) and _outward(f)[2] < -0.99 and _near(f.pointOnFace.z / MM, -W):
            if face is None or f.area > face.area:
                face = f
    # extruir la cara directamente falla ("la ruta es tangente al perfil"); con un boceto en ella, que trae sus
    # aristas proyectadas, sí: el anillo es el perfil con dos lazos (el otro es el disco del rebaje)
    sk = _sketch(comp, face, 'Anillo del soporte')
    sk.isVisible = False
    ring = [pr for pr in sk.profiles if pr.profileLoops.count == 2][0]
    wall = _extrude(comp, ring, lay.w_bed - W, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, 'Soporte')
    support = wall.bodies.item(0)
    # ala: del borde de dentro del anillo a un círculo SUPPORT_BRIM por fuera de la rueda
    bottom = [f for f in support.faces if isinstance(f.geometry, adsk.core.Plane) and _outward(f)[2] < -0.99][0]
    inner = [lp for lp in bottom.loops if not lp.isOuter][0]
    sk = _sketch(comp, _plane_at(comp, comp.xYConstructionPlane, -lay.w_bed, 'Cama de la rueda'), 'Ala del soporte')
    sk.isComputeDeferred = True
    for e in inner.edges:
        sk.project(e)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(P(0, 0, -lay.w_bed)),
                                                    (lay.q['rim'] + SUPPORT_BRIM) * MM)
    sk.isComputeDeferred = False
    sk.isVisible = False
    prof = [pr for pr in sk.profiles if pr.profileLoops.count == 2][0]
    brim = _extrude(comp, prof, SUPPORT_BRIM_T, adsk.fusion.FeatureOperations.JoinFeatureOperation, 'Ala del soporte',
                    [support])
    support = brim.bodies.item(0)
    support.name = 'Soporte'
    support.isLightBulbOn = False
    return support


def add_wheel_shafts(comp, body, lay):
    """Ejes de la rueda: revolución alrededor de su eje Z, unida a la rueda."""
    polys = [[(r, 0, s) for s, r in closed(p)] for p in lay.wheel_shaft_profiles()]
    f, _ = _revolve(comp, comp.xZConstructionPlane, polys, ((0, 0, -100), (0, 0, 100)),
                    adsk.fusion.FeatureOperations.JoinFeatureOperation, 'Ejes', [body])
    return f.bodies.item(0)


def add_worm_shafts(comp, body, lay):
    """Ejes y pomo del sinfín: revolución alrededor de su eje X (por y = A), unida al sinfín, y estrías del pomo
    (una extrusión de corte y un patrón circular)."""
    A = lay.A
    profiles, (k0, k1) = lay.worm_shaft_profiles()
    polys = [[(s, A + r, 0) for s, r in closed(p)] for p in profiles]
    f, axis_line = _revolve(comp, comp.xYConstructionPlane, polys, ((-200, A, 0), (200, A, 0)),
                            adsk.fusion.FeatureOperations.JoinFeatureOperation, 'Ejes y pomo', [body])
    body = f.bodies.item(0)
    # una estría: rombo en la sección del pomo (a +Y del eje), extruido a lo largo del pomo. Por el lado del sinfín
    # se mete 1.5 mm en el cono de 45°, para que la estría salga por el cono sin dejar una cara plana al final;
    # por el otro, sale por el extremo del pomo
    lo, hi = k1 - 2, k0 + 1.5
    xm = (lo + hi) / 2
    pl = _plane_at(comp, comp.yZConstructionPlane, xm, 'Pomo')
    sk = _sketch(comp, pl, 'Estría')
    kr = KNOB_D / 2
    _poly(sk, [(xm, A + kr + v, u) for u, v in diamond(KNOB_GROOVE)])
    sk.isVisible = False
    groove = _extrude(comp, _all_profiles(sk), hi - lo, adsk.fusion.FeatureOperations.CutFeatureOperation,
                      'Estría', [body], symmetric=True)
    oc = adsk.core.ObjectCollection.create()
    oc.add(groove)
    pin = comp.features.circularPatternFeatures.createInput(oc, axis_line)
    pin.quantity = adsk.core.ValueInput.createByReal(KNOB_GROOVES)
    pin.totalAngle = adsk.core.ValueInput.createByString('360 deg')
    pat = comp.features.circularPatternFeatures.add(pin)
    pat.name = 'Estrías'
    return comp.bRepBodies.item(0)


# ---------------------------------------------------------------- montaje en Fusion
def _mark(occ, role):
    occ.attributes.add(ATTR, 'role', role)


def clear(design):
    """Borra lo que creó una ejecución anterior."""
    root = design.rootComponent
    for coll in (root.motionLinks, root.joints, root.rigidGroups):
        for i in range(coll.count - 1, -1, -1):
            it = coll.item(i)
            if it.name.startswith('Demo'):
                it.deleteMe()
    for i in range(root.occurrences.count - 1, -1, -1):
        occ = root.occurrences.item(i)
        if occ.attributes.itemByName(ATTR, 'role'):
            occ.deleteMe()


def _dish(comp, body, q, lay):
    """Rebaje de la cara z = -W: solevación entre el contorno desfasado (prolongado 0.5 mm por fuera de la
    cara) y el mismo contorno DISH_DEPTH más adentro, y corte. Se soleva un sector de un diente y se repite
    alrededor (con el contorno entero de una vez, Fusion tarda más de 10 minutos)."""
    W = q['wheel_width'] / 2
    period = lay.dish_contour()
    pitch = 2 * math.pi / q['teeth']
    th0 = period[0][0]
    # el sector se cierra con el primer punto del diente siguiente, que tiene el mismo radio
    period = period + [(th0 + pitch, period[0][1])]
    r_in = 0.5   # el vértice del sector, dentro del cono del eje
    sketches = []
    for z, dr in ((-W - 0.5, 0.5), (-W + DISH_DEPTH, -DISH_DEPTH)):
        pin = comp.constructionPlanes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z * MM))
        pl = comp.constructionPlanes.add(pin)
        pl.isLightBulbOn = False
        sk = comp.sketches.add(pl)
        sk.name = 'Rebaje z=%+.1f' % z
        sk.isComputeDeferred = True

        def sp(r, t):
            return sk.modelToSketchSpace(P(r * math.sin(t), r * math.cos(t), z))
        pts = adsk.core.ObjectCollection.create()
        for th, r in period:
            pts.add(sp(r + dr, th))
        spl = sk.sketchCurves.sketchFittedSplines.add(pts)
        lines = sk.sketchCurves.sketchLines
        t1 = th0 + pitch
        l0 = lines.addByTwoPoints(sp(r_in, th0), spl.startSketchPoint)
        l1 = lines.addByTwoPoints(spl.endSketchPoint, sp(r_in, t1))
        sk.sketchCurves.sketchArcs.addByThreePoints(l1.endSketchPoint, sp(r_in, th0 + pitch / 2), l0.startSketchPoint)
        sk.isComputeDeferred = False
        sk.isVisible = False
        if sk.profiles.count != 1:
            raise RuntimeError('El sector del rebaje no ha salido cerrado (%d perfiles).' % sk.profiles.count)
        sketches.append(sk)
    li = comp.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    for sk in sketches:
        li.loftSections.add(sk.profiles.item(0))
    li.isSolid = True
    loft = comp.features.loftFeatures.add(li)
    loft.name = 'Rebaje (un diente)'
    sector = loft.bodies.item(0)
    oc = adsk.core.ObjectCollection.create()
    oc.add(sector)
    pin = comp.features.circularPatternFeatures.createInput(oc, comp.zConstructionAxis)
    pin.quantity = adsk.core.ValueInput.createByReal(q['teeth'])
    pin.totalAngle = adsk.core.ValueInput.createByString('360 deg')
    pat = comp.features.circularPatternFeatures.add(pin)
    pat.name = 'Rebaje'
    tools = adsk.core.ObjectCollection.create()
    tools.add(sector)
    for b in pat.bodies:
        if b != sector:
            tools.add(b)
    ci = comp.features.combineFeatures.createInput(body, tools)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    cf = comp.features.combineFeatures.add(ci)
    cf.name = 'Rebaje'
    return cf.bodies.item(0)


def _appearance(design, name):
    """Aspecto de plástico mate con el color de COLORS (copia de 'Plástico - Mate (blanco)'), o None."""
    ap = design.appearances.itemByName(name)
    if ap:
        return ap
    app = adsk.core.Application.get()
    for lib in app.materialLibraries:
        try:
            src = lib.appearances.itemById('Prism-127')
        except Exception:
            src = None
        if src:
            ap = design.appearances.addByCopy(src, name)
            for pid in ('opaque_albedo', 'surface_albedo'):
                prop = ap.appearanceProperties.itemById(pid)
                if prop:
                    try:
                        prop.value = adsk.core.Color.create(*COLORS[name], 255)
                    except Exception:
                        pass
            return ap
    return None


def _paint(design, occs, name):
    ap = _appearance(design, name)
    if ap is None:
        return
    for o in occs:
        # también en la ocurrencia: el sinfín y la rueda se rehacen al recalcular la línea de tiempo (por ejemplo,
        # al borrar un boceto anterior) y pierden el aspecto puesto en el cuerpo
        o.appearance = ap
        for b in o.component.bRepBodies:
            b.appearance = ap


def _free(occ):
    for attr in ('isGroundToParent', 'isGrounded'):
        try:
            setattr(occ, attr, False)
        except Exception:
            pass


def _revolute(root, occ_fixed, fixed_line, occ_moving, moving_line, name):
    fixed = fixed_line.createForAssemblyContext(occ_fixed)
    moving = moving_line.createForAssemblyContext(occ_moving)
    ji = root.joints.createInput(
        adsk.fusion.JointGeometry.createByCurve(moving, adsk.fusion.JointKeyPointTypes.MiddleKeyPoint),
        adsk.fusion.JointGeometry.createByCurve(fixed, adsk.fusion.JointKeyPointTypes.MiddleKeyPoint))
    ji.setAsRevoluteJointMotion(adsk.fusion.JointDirections.CustomJointDirection, fixed)
    j = root.joints.add(ji)
    j.name = name
    return j


def _rigid(root, occs, name):
    oc = adsk.core.ObjectCollection.create()
    for o in occs:
        oc.add(o)
    g = root.rigidGroups.add(oc, False)
    g.name = name
    return g


def build_demo(design):
    """Crea la demo en el diseño. Devuelve (log, piezas, q) con piezas = {nombre: (ocurrencia, cuerpo)}."""
    log = []
    if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
        raise RuntimeError('La demo necesita un diseño con historial (paramétrico).')
    for mod in (wormgear.geometry, wormgear.build, wormgear.check):
        importlib.reload(mod)
    q, errors, warns, summary = G.check_params(GEAR)
    if errors:
        raise ValueError('\n'.join(errors))
    lay = Layout(q)
    root = design.rootComponent
    clear(design)
    tl = design.timeline
    start = tl.count
    parts = {}

    # sinfín y rueda de WormGear con sus ejes, colocados con la matriz WG
    M = wg_matrix()
    tag = 'm%g %d:%d' % (q['module'], q['teeth'], q['starts'])
    occ_worm = root.occurrences.addNewComponent(M)
    occ_worm.component.name = 'Sinfín %s' % tag
    _mark(occ_worm, 'worm')
    worm = B.build_worm(occ_worm.component, q, log)
    worm = add_worm_shafts(occ_worm.component, worm, lay)
    worm.name = 'Sinfín'
    occ_wheel = root.occurrences.addNewComponent(M)
    occ_wheel.component.name = 'Rueda %s' % tag
    _mark(occ_wheel, 'wheel')
    wheel = B.build_wheel(occ_wheel.component, q, log)
    wheel = _dish(occ_wheel.component, wheel, q, lay)
    wheel = add_wheel_shafts(occ_wheel.component, wheel, lay)
    wheel = add_wheel_arrow(occ_wheel.component, wheel, lay)
    wheel.name = 'Rueda'
    support = add_wheel_support(occ_wheel.component, wheel, lay)
    parts['sinfin'] = (occ_worm, worm)
    parts['rueda'] = (occ_wheel, wheel)

    # base y tapas
    occ_base = build_base(root, lay)
    caps = build_caps(root, lay)
    parts['base'] = (occ_base, occ_base.component.bRepBodies.item(0))
    parts['tapa'] = (caps[0], caps[0].component.bRepBodies.item(0))

    _paint(design, [occ_worm, occ_wheel], 'Demo morado')
    _paint(design, caps, 'Demo turquesa')
    _paint(design, [occ_base], 'Demo blanco')

    # juntas: base fija con sus tapas; sinfín y rueda giran con el enlace de movimiento
    occ_base.isGrounded = True
    _rigid(root, [occ_base] + caps, 'Demo base')
    for o in (occ_worm, occ_wheel):
        _free(o)
    # las líneas fijas van en un componente "Ejes" colocado con la misma matriz WG: así la junta ve la misma
    # geometría en las dos piezas y no gira el sinfín alrededor de su eje al crearse (lo desfasaría)
    occ_axes = root.occurrences.addNewComponent(M)
    occ_axes.component.name = 'Ejes %s' % tag
    _mark(occ_axes, 'axes')
    occ_axes.isGrounded = True
    j_worm = _revolute(root, occ_axes, B._axis_line(occ_axes.component, 'worm', q),
                       occ_worm, B._axis_line(occ_worm.component, 'worm', q), 'Demo giro sinfín')
    j_wheel = _revolute(root, occ_axes, B._axis_line(occ_axes.component, 'wheel', q),
                        occ_wheel, B._axis_line(occ_wheel.component, 'wheel', q), 'Demo giro rueda')
    mi = root.motionLinks.createInput(j_worm, j_wheel)
    mi.valueOne = adsk.core.ValueInput.createByString('360 deg')
    mi.valueTwo = adsk.core.ValueInput.createByString('%.6f deg' % (360.0 * q['starts'] / q['teeth']))
    mi.isReversed = q['hand'] < 0
    ml = root.motionLinks.add(mi)
    ml.name = 'Demo sinfín'
    # el número de pieza es el nombre que sale en el árbol de un STEP (por defecto, la fecha de creación)
    for o in root.occurrences:
        if o.attributes.itemByName(ATTR, 'role'):
            o.component.partNumber = o.component.name
    try:
        if tl.count - 1 > start:
            grp = tl.timelineGroups.add(start, tl.count - 1)
            grp.name = 'Demo WormGear'
    except Exception as e:
        log.append('No se pudo agrupar la línea de tiempo (%s).' % str(e).splitlines()[0])
    log.append('Demo: A = %.1f mm, rueda Ø%.1f a z = %.1f, sinfín Ø%.1f a z = %.1f'
               % (q['A'], 2 * q['rim'], H, 2 * q['r_tip'], lay.Hw))
    for k, (o, b) in parts.items():
        log.append('  %-8s %8.0f mm³' % (k, b.volume * 1000))
    log.append('  soporte  %8.0f mm³, %.1f mm de alto' % (support.volume * 1000, lay.w_bed - lay.w_face))
    return log, parts, q


def overhang(body, limit_deg=45.0):
    """Área (mm²) que mira hacia abajo con menos de limit_deg sobre la horizontal (el umbral de voladizo del
    laminador), sin contar lo que apoya en la cama. El cuerpo tiene que estar en su postura de impresión."""
    mc = body.meshManager.createMeshCalculator()
    mc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
    mesh = mc.calculate()
    co = mesh.nodeCoordinatesAsDouble
    idx = mesh.nodeIndices
    z0 = body.boundingBox.minPoint.z
    lim = -math.cos(math.radians(limit_deg)) - 0.02
    area = 0.0
    for i in range(0, len(idx), 3):
        a, b, c = (co[3 * idx[i + j]:3 * idx[i + j] + 3] for j in range(3))
        n = cross([b[k] - a[k] for k in range(3)], [c[k] - a[k] for k in range(3)])
        ln = math.sqrt(sum(x * x for x in n))
        if ln == 0:
            continue
        if n[2] / ln < lim and (a[2] + b[2] + c[2]) / 3 - z0 > 0.02 * MM:
            area += ln / 2
    return area * 100.0   # cm² -> mm²


def interference(design, occs):
    """Choques entre las piezas montadas: [(pieza, pieza, mm³)]. Sin el soporte de la rueda, que solo sirve
    para imprimirla."""
    oc = adsk.core.ObjectCollection.create()
    for o in occs:
        for b in o.bRepBodies:
            if b.name != 'Soporte':
                oc.add(b)
    ii = design.createInterferenceInput(oc)
    ii.areCoincidentFacesIncluded = False
    res = design.analyzeInterference(ii)

    def nm(e):
        return e.assemblyContext.name if getattr(e, 'assemblyContext', None) else e.name
    return [(nm(r.entityOne), nm(r.entityTwo), r.interferenceBody.volume * 1000) for r in res]


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        log, parts, q = build_demo(design)
        ui.messageBox('\n'.join(log), 'Demo WormGear')
    except Exception:
        if ui:
            ui.messageBox(traceback.format_exc(), 'Demo WormGear')
