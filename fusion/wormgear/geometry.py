# Matemática del sinfín y su rueda, sin dependencias de Fusion (se puede probar con Python normal).
# Unidades: mm y radianes.
#
# Convenios (marco del mundo):
#   - rueda: eje Z, centro en el origen, plano medio z = 0;
#   - sinfín: eje paralelo a X, por (0, A, 0); hélice a derechas con el centro del filete en
#     x = lead·(t - π)/2π, siendo t el ángulo alrededor del eje desde +Y hacia +Z.
#     Con esta fase, en el plano medio el filete queda centrado en x = 0 justo debajo, frente a la rueda.
#   - a izquierdas: todo se calcula a derechas y se toma el simétrico respecto al plano x = 0 (el eje del
#     sinfín está en ese plano). El simétrico de un engrane bueno es otro engrane bueno; el giro de la rueda
#     cambia de sentido (el del sinfín no).
#
# Rueda lisa: en cada plano z = c, el flanco del cortador (sinfín engordado) es
#   x(u) = lead·atan2(-c, -u)/2π + σ·hw(r),   y = A + u,   r = √(u² + c²)
# Girar el sinfín equivale a desplazar esa curva en x (es un helicoide), y la rueda gira alrededor de Z,
# así que el plano no se mueve: la envolvente 2D de cada plano es la del engrane 3D real.
# Movimiento en el marco de la rueda (rodadura sobre el primitivo):  Q = Rot(-θ)·(x - R2·θ, y)
# Ecuación de engrane (la normal pasa por el punto primitivo):  θ = (x + (y - R2)/x') / R2

import math

try:
    from .i18n import tr
except ImportError:   # python geometry.py, sin paquete
    from i18n import tr

DEFAULTS = dict(
    module=1.5,          # módulo (mm)
    starts=1,            # entradas del sinfín
    teeth=30,            # dientes de la rueda
    worm_pitch_d=16.0,   # diámetro primitivo del sinfín (mm)
    flank_deg=45.0,      # ángulo de flanco axial (45 = sin voladizos con el sinfín de pie)
    addendum_f=0.5,      # cabeza (× módulo)
    dedendum_f=0.6,      # pie (× módulo)
    clearance=0.15,      # holgura radial (mm)
    backlash=0.1,        # holgura entre flancos, axial (mm)
    worm_length=30.0,
    worm_bore=5.1,
    wheel_width=10.0,
    wheel_bore=8.1,
    rim_over_tip=0.63,   # borde exterior de la rueda por encima de la cabeza de la garganta (mm)
    sections=23,         # perfiles de la solevación
    left_handed=False,   # sinfín a izquierdas (y su rueda): el simétrico respecto al plano x = 0
    thread_length=0.0,   # longitud con filete, centrada (0 = todo el sinfín); el resto son tramos lisos
    shoulder_d=0.0,      # Ø de los tramos lisos (0 = fondo del filete - 2·CHAMFER_BELOW_ROOT)
    worm_bore_shape='round',
    worm_bore_flat=4.6,  # plano en D: distancia del plano al lado opuesto (eje de 5 con plano a 4.5 + 0.1)
    wheel_bore_shape='round',
    wheel_bore_flat=7.6,
)

# formas de taladro: (clave, etiqueta). El tamaño es el Ø (redondo, D, chavetero) o la medida entre caras.
BORE_SHAPES = [('round', 'Redondo'), ('d', 'Plano en D'), ('hex', 'Hexagonal'), ('square', 'Cuadrado'),
               ('keyway', 'Chavetero DIN 6885')]
# chavetero DIN 6885 en el cubo: (Ø del eje hasta, ancho b, profundidad t2 en el cubo)
DIN6885 = [(8, 2, 1.0), (10, 3, 1.4), (12, 4, 1.8), (17, 5, 2.3), (22, 6, 2.8), (30, 8, 3.3), (38, 10, 3.3),
           (44, 12, 3.3), (50, 14, 3.8), (58, 16, 4.3), (65, 18, 4.4)]
FIT = 0.1               # holgura de impresión que se añade al chavetero (mm)
CHAMFER_BELOW_ROOT = 0.3   # los chaflanes del sinfín empiezan 0.3 mm por debajo del fondo del filete (mm)
CHAMFER_TOP = 0.5          # y suben hasta 0.5 mm por encima de la cresta (mm)
# rozamiento entre flancos de plástico impreso (PLA, PETG): con grasa y en seco
MU_GREASED = 0.1
MU_DRY = 0.3


def derive(prm):
    """Añade las medidas derivadas a una copia de los parámetros."""
    q = dict(DEFAULTS)
    q.update(prm)
    m = q['module']
    q['p'] = math.pi * m                       # paso axial
    q['lead'] = q['starts'] * q['p']           # avance
    q['R1'] = q['worm_pitch_d'] / 2
    q['R2'] = m * q['teeth'] / 2
    q['A'] = q['R1'] + q['R2']                 # distancia entre ejes
    q['ha'] = q['addendum_f'] * m
    q['hf'] = q['dedendum_f'] * m
    q['alpha'] = math.radians(q['flank_deg'])
    q['r_tip'] = q['R1'] + q['ha']
    q['r_root'] = q['R1'] - q['hf']
    q['hob_tip'] = q['r_tip'] + q['clearance']
    q['r_tip2'] = q['A'] - q['r_root'] - q['clearance']   # cabeza de la rueda en el plano medio
    q['throat'] = q['r_root'] + q['clearance']            # radio de la garganta
    q['rim'] = q['r_tip2'] + q['rim_over_tip']
    q['R_OUT'] = q['rim'] + 1.0
    q['lead_angle_deg'] = math.degrees(math.atan(q['lead'] / (math.pi * q['worm_pitch_d'])))
    # ángulo de presión normal: el flanco es recto en la sección axial, tan αn = tan αx · cos λ
    q['alpha_n'] = math.atan(math.tan(q['alpha']) * math.cos(math.radians(q['lead_angle_deg'])))
    q['hand'] = -1 if q['left_handed'] else 1
    # sinfín: filete en |x| <= thread_half; fuera, tramos lisos de radio r_shoulder
    L = q['worm_length'] / 2
    tl = q['thread_length']
    q['thread_half'] = L if tl <= 0 or tl >= q['worm_length'] else tl / 2
    q['r_chamfer'] = q['r_root'] - CHAMFER_BELOW_ROOT
    q['r_shoulder'] = q['shoulder_d'] / 2 if q['shoulder_d'] > 0 else q['r_chamfer']
    # hasta dónde (en x) llega la rueda dentro del cilindro de cresta del sinfín (en el plano medio)
    q['x_contact'] = math.sqrt(max(q['rim'] ** 2 - (q['A'] - q['r_tip']) ** 2, 0.0))
    # hasta dónde (en z) llega el cortador a la rueda: el fondo del hueco, A - √(cabeza² - z²), sube con |z|
    # y deja de tocar el disco cuando pasa del borde (c_touch). Las secciones llegan medio mm más allá de
    # las caras para que el corte salga limpio, pero no más allá de donde el hueco aún existe (c_lim).
    q['c_touch'] = math.sqrt(max(q['hob_tip'] ** 2 - (q['A'] - q['rim']) ** 2, 0.0))
    q['c_lim'] = math.sqrt(max(q['hob_tip'] ** 2 - (q['A'] - q['R_OUT'] + 0.2) ** 2, 0.0))
    w = min(q['wheel_width'] / 2 + 0.5, q['c_lim'])
    q['section_z'] = [-w + 2 * w * i / (q['sections'] - 1) for i in range(q['sections'])]
    # chaflán de 45° en las caras: empieza donde el diente baja de la mitad de su altura del centro, para
    # quitar las puntas bajas y débiles de los bordes. chamfer_z = None si los dientes llegan bien a las caras.
    q['chamfer_z'] = q['chamfer_r'] = None
    d0 = tooth_depth(q, 0.0)
    W = q['wheel_width'] / 2
    n = 400
    for i in range(n + 1):
        z = W * i / n
        if tooth_depth(q, z) < 0.5 * d0:
            if W - z >= 0.3:   # un chaflán de menos de 0.3 mm no aporta y solo añade caras
                q['chamfer_z'] = z
                q['chamfer_r'] = _outer_radius(q, z)
            break
    return q


def _outer_radius(q, z):
    """Borde del disco sin chaflán: garganta toroidal limitada por el borde."""
    t = q['throat']
    if abs(z) < t:
        return min(q['rim'], q['A'] - math.sqrt(t * t - z * z))
    return q['rim']


def tooth_depth(q, z):
    """Altura del diente de la rueda en z: del fondo que deja el cortador al borde del disco (0 si no llega)."""
    if abs(z) >= q['hob_tip']:
        return 0.0
    return max(0.0, _outer_radius(q, z) - root_radius(q, z))


def hw(q, r, extra=0.0):
    """Semiancho axial del filete a radio r (extra = engorde de cada flanco)."""
    return q['p'] / 4 + extra - (r - q['R1']) * math.tan(q['alpha'])


def efficiency(q, mu):
    """Rendimiento con rozamiento mu: (el sinfín mueve la rueda, la rueda mueve el sinfín).

    El segundo es ≤ 0 si la rueda no puede mover el sinfín (autobloqueo): tan λ ≤ mu / cos αn.
    Con más ángulo de flanco, cos αn baja y el rozamiento pesa más: 45° rinde menos que 20°, pero
    se autobloquea con más hélice.
    """
    t = math.tan(math.radians(q['lead_angle_deg']))
    c = math.cos(q['alpha_n'])
    return (c - mu * t) / (c + mu / t), (c - mu / t) / (c + mu * t)


def locking_limit_deg(q, mu):
    """Ángulo de hélice hasta el que la rueda no puede mover el sinfín con rozamiento mu."""
    return math.degrees(math.atan(mu / math.cos(q['alpha_n'])))


def rim_radius(q, z):
    """Radio exterior de la rueda a la altura z: garganta toroidal, limitada por el borde y por el chaflán."""
    r = _outer_radius(q, z)
    if q['chamfer_z'] is not None and abs(z) > q['chamfer_z']:
        r = min(r, q['chamfer_r'] - (abs(z) - q['chamfer_z']))
    return r


def _rot(a, x, y):
    ca, sa = math.cos(a), math.sin(a)
    return (ca * x - sa * y, sa * x + ca * y)


def envelope_point(q, c, u, sigma):
    """Punto de la envolvente generado por el punto u del flanco sigma (-1 izquierdo, +1 derecho) del cortador."""
    ta = math.tan(q['alpha'])
    r = math.hypot(u, c)
    x = q['lead'] * math.atan2(-c, -u) / (2 * math.pi) + sigma * hw(q, r, q['backlash'] / 2)
    y = q['A'] + u
    dx = -q['lead'] * c / (2 * math.pi * r * r) - sigma * ta * u / r
    theta = (x + (y - q['R2']) / dx) / q['R2']
    return _rot(-theta, x - q['R2'] * theta, y)


def root_radius(q, c):
    """Fondo del hueco en el plano z=c: lo marca la cabeza del cortador."""
    return q['A'] - math.sqrt(q['hob_tip'] ** 2 - c * c)


def flank(q, c, sigma, n=40):
    """Puntos de un flanco del hueco, del círculo de fondo a R_OUT (radio creciente), remuestreados a n+1.
    El hueco es lo que barre el cortador: a cada radio, el flanco está donde más entra en el diente, entre
    - la envolvente del flanco del cortador, desde la cabeza; por encima del fondo se prolonga (virtual),
      porque por fuera del borde de la rueda no hay material que cortar;
    - la trocoide de la esquina de la cabeza, que es la que talla el pie del diente. Con poco ángulo de flanco
      la envolvente no baja hasta el fondo y, sin la trocoide, la cresta del sinfín rozaba ahí la rueda.
    La esquina está en y = A - √(hob_tip² - c²) = rr, así que su trocoide sale del círculo de fondo: con
    X = x_esquina - R2·θ, el punto está a radio √(X² + rr²) y a un ángulo atan2(X, rr) + θ desde +Y.
    A cada radio hay dos puntos, con ±X, y vale el que más entra en el diente: cuál es cambia según el fondo quede
    por debajo o por encima de R2. Con solo uno, en los extremos de la rueda quedaba un escalón en el pie."""
    rr = root_radius(q, c)
    span = q['R_OUT'] - rr
    u0 = -math.sqrt(q['hob_tip'] ** 2 - c * c)   # cabeza del cortador
    x0 = q['lead'] * math.atan2(-c, -u0) / (2 * math.pi) + sigma * hw(q, q['hob_tip'], q['backlash'] / 2)
    # radios más juntos cerca del fondo, donde la trocoide cambia deprisa de ángulo
    N = 400
    radii = [rr + span * (k / N) ** 2 for k in range(N + 1)]
    best = []
    for r in radii:
        X = math.sqrt(max(r * r - rr * rr, 0.0))
        best.append(max(math.atan2(X, rr) + (x0 - X) / q['R2'], math.atan2(-X, rr) + (x0 + X) / q['R2'],
                        key=lambda a: sigma * a))
    u1 = -0.2
    steps = 400
    prev = None
    found = 0
    for i in range(steps + 1):
        u = u0 + (u1 - u0) * i / steps
        try:
            e = envelope_point(q, c, u, sigma)
        except ZeroDivisionError:   # flanco paralelo a la rodadura: ese punto no engendra nada
            prev = None
            continue
        cur = (math.hypot(*e), angle_from_y(e))
        found += 1
        if prev is not None and cur[0] != prev[0]:
            lo, hi = min(prev[0], cur[0]), max(prev[0], cur[0])
            k0 = math.ceil(N * math.sqrt(max(lo - rr, 0.0) / span))
            k1 = min(N, math.floor(N * math.sqrt(max(hi - rr, 0.0) / span)))
            for k in range(k0, k1 + 1):
                a = prev[1] + (radii[k] - prev[0]) / (cur[0] - prev[0]) * (cur[1] - prev[1])
                if sigma * a > sigma * best[k]:
                    best[k] = a
        prev = cur
    if found < 2:
        raise ValueError(tr('no se pudo calcular el flanco en z=%.2f') % c)
    pts = [(r * math.sin(a), r * math.cos(a)) for r, a in zip(radii, best)]
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    res = []
    j = 0
    for i in range(n + 1):
        s = L[-1] * i / n
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        t = 0 if L[j + 1] == L[j] else (s - L[j]) / (L[j + 1] - L[j])
        res.append((pts[j][0] + t * (pts[j + 1][0] - pts[j][0]), pts[j][1] + t * (pts[j + 1][1] - pts[j][1])))
    return res


def gap_profile(q, c, n=40):
    """Hueco de un diente en z=c: (flanco izquierdo, flanco derecho, radio de fondo, radio exterior).
    Los flancos van del fondo hacia fuera. El hueco está centrado en +Y.
    A izquierdas, el simétrico respecto al plano x = 0: los flancos espejados e intercambiados."""
    left, right = flank(q, c, -1, n), flank(q, c, +1, n)
    if q['hand'] < 0:
        left, right = [(-x, y) for x, y in right], [(-x, y) for x, y in left]
    return left, right, root_radius(q, c), q['R_OUT']


# ---------------------------------------------------------------- silueta del sinfín y taladros

def worm_outline(q):
    """Silueta del sinfín [(x, r)] de -L a +L, para recortar el filete por revolución alrededor de su eje:
    chaflanes de 45° desde un poco por debajo del fondo hasta por encima de la cresta en los extremos del
    filete y, si los hay, tramos lisos de radio r_shoulder (con un escalón de 45° si son más finos)."""
    L, T = q['worm_length'] / 2, q['thread_half']
    r0, rs = q['r_chamfer'], q['r_shoulder']
    top = q['r_tip'] + CHAMFER_TOP
    ch = top - r0
    pts = [(-T, r0), (-T + ch, top), (T - ch, top), (T, r0)]
    if T < L:
        step = r0 - rs
        pts = [(-L, rs), (-T - step, rs)] + pts + [(T + step, rs), (L, rs)]
    out = []
    for p in pts:   # sin puntos repetidos (escalón de largo 0)
        if not out or abs(p[0] - out[-1][0]) > 1e-9 or abs(p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    return out


def _keyway(size):
    """(ancho, radio del fondo) del chavetero DIN 6885 del cubo para un taladro de Ø size, o None."""
    d = round(size)
    if d <= 6:
        return None
    for d_max, b, t2 in DIN6885:
        if d <= d_max:
            return b + FIT, d / 2 + t2 + FIT
    return None


def bore_error(shape, size, flat):
    """Por qué no se puede hacer ese taladro, o None."""
    if shape not in dict(BORE_SHAPES):
        return tr('forma de taladro desconocida (%s)') % shape
    if size <= 0:
        return None
    if shape == 'd' and not size / 2 < flat < size:
        return tr('el plano en D tiene que estar entre %.2f y %.2f mm del lado opuesto') % (size / 2, size)
    if shape == 'keyway':
        k = _keyway(size)
        if k is None:
            return tr('el chavetero DIN 6885 va de Ø6 a Ø65')
        if k[0] / 2 >= size / 2:
            return tr('el chavetero es más ancho que el taladro')
    return None


def bore_radius(shape, size, flat):
    """Distancia máxima del taladro a su centro (0 = sin taladro)."""
    if size <= 0:
        return 0.0
    if shape == 'hex':
        return size / math.sqrt(3)
    if shape == 'square':
        return size / math.sqrt(2)
    if shape == 'keyway':
        k = _keyway(size)
        if k:
            return math.hypot(k[0] / 2, k[1])
    return size / 2


def bore_outline(shape, size, flat):
    """Contorno del taladro centrado en el origen (u, v): [('circle', r)] o una lista cerrada de
    ('line', p0, p1) / ('arc', p0, p_medio, p1). Vacío si no hay taladro. El plano en D y el chavetero
    quedan hacia +v."""
    if size <= 0:
        return []
    r = size / 2
    if shape == 'hex':
        R = size / math.sqrt(3)
        pts = [(R * math.cos(math.pi * k / 3), R * math.sin(math.pi * k / 3)) for k in range(6)]
    elif shape == 'square':
        pts = [(r, r), (-r, r), (-r, -r), (r, -r)]
    elif shape == 'd':
        v0 = flat - r
        u0 = math.sqrt(r * r - v0 * v0)
        return [('line', (u0, v0), (-u0, v0)), ('arc', (-u0, v0), (0.0, -r), (u0, v0))]
    elif shape == 'keyway' and _keyway(size):
        w, vk = _keyway(size)
        w /= 2
        vc = math.sqrt(r * r - w * w)
        return [('line', (w, vc), (w, vk)), ('line', (w, vk), (-w, vk)), ('line', (-w, vk), (-w, vc)),
                ('arc', (-w, vc), (0.0, -r), (w, vc))]
    else:
        return [('circle', r)]
    return [('line', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def bores(q):
    """Contornos del taladro del sinfín y de la rueda."""
    return (bore_outline(q['worm_bore_shape'], q['worm_bore'], q['worm_bore_flat']),
            bore_outline(q['wheel_bore_shape'], q['wheel_bore'], q['wheel_bore_flat']))


def angle_from_y(pt):
    return math.atan2(pt[0], pt[1])


def _angle_at_radius(pts, r):
    for a, b in zip(pts, pts[1:]):
        ra, rb = math.hypot(*a), math.hypot(*b)
        if ra <= r <= rb and rb > ra:
            t = (r - ra) / (rb - ra)
            return angle_from_y((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return None


def tip_land(q):
    """Grosor mínimo (mm) de la cabeza del diente de la rueda en su borde exterior, mirando todas las secciones."""
    pitch = 2 * math.pi / q['teeth']
    worst = None
    for c in q['section_z']:
        if abs(c) > q['wheel_width'] / 2:
            continue
        left, right, _, _ = gap_profile(q, c, 60)
        rr = rim_radius(q, c)
        al, ar = _angle_at_radius(left, rr), _angle_at_radius(right, rr)
        if al is None or ar is None:
            continue
        land = (pitch - (ar - al)) * rr
        worst = land if worst is None else min(worst, land)
    return worst


def check_params(prm):
    """Devuelve (q, errores, avisos, resumen) para el diálogo."""
    q = derive(prm)
    errors, warns = [], []
    if q['starts'] < 1 or q['teeth'] < 3:
        errors.append(tr('Entradas ≥ 1 y dientes ≥ 3.'))
    for part, name in (('worm', 'Taladro del sinfín'), ('wheel', 'Taladro de la rueda')):
        e = bore_error(q[part + '_bore_shape'], q[part + '_bore'], q[part + '_bore_flat'])
        if e:
            errors.append('%s: %s.' % (tr(name), e))
    rb_worm = bore_radius(q['worm_bore_shape'], q['worm_bore'], q['worm_bore_flat'])
    rb_wheel = bore_radius(q['wheel_bore_shape'], q['wheel_bore'], q['wheel_bore_flat'])
    partial = q['thread_half'] < q['worm_length'] / 2
    if q['r_root'] <= rb_worm + 0.8:
        errors.append(tr('El taladro del sinfín no cabe: pared de %.2f mm bajo el fondo del filete.') % (q['r_root'] - rb_worm))
    if partial:
        L, T = q['worm_length'] / 2, q['thread_half']
        if q['r_shoulder'] > q['r_chamfer'] + 1e-9:
            errors.append(tr('Los tramos lisos pueden tener como mucho Ø%.2f (el fondo del filete menos %.1f mm).')
                          % (2 * q['r_chamfer'], 2 * CHAMFER_BELOW_ROOT))
        elif q['r_shoulder'] <= rb_worm + 0.8:
            errors.append(tr('El taladro del sinfín no cabe en los tramos lisos: pared de %.2f mm.') % (q['r_shoulder'] - rb_worm))
        elif L - T < q['r_chamfer'] - q['r_shoulder'] + 0.5:
            errors.append(tr('Los tramos lisos son demasiado cortos para el escalón de 45° hasta Ø%.2f: '
                          'acorta el filete o alarga el sinfín.') % (2 * q['r_shoulder']))
    # el filete entero (sin chaflán) tiene que cubrir toda la zona en la que entra la rueda
    need = 2 * (q['x_contact'] + q['r_tip'] - q['r_chamfer'])
    if 2 * q['thread_half'] < need:
        errors.append(tr('El filete es demasiado corto para la rueda: tiene que medir al menos %.1f mm.') % need)
    if q['wheel_width'] / 2 + 0.5 >= q['hob_tip']:
        errors.append(tr('La rueda es demasiado ancha para este sinfín (ancho/2 tiene que ser < %.1f mm).') % (q['hob_tip'] - 0.5))
    crest = 2 * hw(q, q['r_tip'])
    gap_root = q['p'] - 2 * hw(q, q['r_root'], q['backlash'] / 2)
    if crest <= 0:
        errors.append(tr('El filete del sinfín acaba en punta (cresta %.2f mm): baja la cabeza o el flanco.') % crest)
    elif crest < 0.4:
        warns.append(tr('Cresta del sinfín de %.2f mm (< 0.4).') % crest)
    if gap_root <= 0:
        errors.append(tr('El hueco del sinfín se cierra en el fondo: baja el pie o el flanco.'))
    elif gap_root < 0.3:
        warns.append(tr('Fondo del hueco del sinfín de %.2f mm.') % gap_root)
    if q['flank_deg'] < 45:
        warns.append(tr('Con el sinfín de pie, la cara de abajo del filete queda a %.0f° de la horizontal '
                     '(el umbral de voladizo del laminador; en Cura, %.0f°).') % (q['flank_deg'], 90 - q['flank_deg']))
    if q['wheel_width'] / 2 > q['c_touch']:
        warns.append(tr('Los dientes no llegan a las caras: el sinfín solo toca la rueda en %.1f mm de ancho '
                     '(estrecha la rueda o agranda el sinfín).') % (2 * q['c_touch']))
    elif q['wheel_width'] / 2 > q['throat'] * math.sin(math.radians(45)):
        warns.append(tr('La garganta de la rueda pasa de 45° en las caras: estrecha la rueda o agranda el sinfín.'))
    if q['ha'] + q['clearance'] > q['R2'] * math.sin(q['alpha']) ** 2:
        warns.append(tr('Puede haber socavado en el pie de los dientes de la rueda (pocos dientes para este flanco).'))
    hub = q['A'] - q['hob_tip'] - rb_wheel
    if hub <= 0.8:
        errors.append(tr('El taladro de la rueda no cabe: quedan %.2f mm hasta el fondo de los dientes.') % hub)
    elif hub < 2:
        warns.append(tr('Queda poco cubo entre el taladro y el fondo de los dientes (%.1f mm).') % hub)
    land = None
    if not errors:
        try:
            land = tip_land(q)
        except ValueError as e:
            errors.append(str(e))
    if land is not None and land < 0.3:
        warns.append(tr('Los dientes de la rueda quedan en punta en el borde (%.2f mm): baja "borde sobre la cabeza".') % land)
    eta_g, eta_d = efficiency(q, MU_GREASED)[0], efficiency(q, MU_DRY)[0]
    lim_g, lim_d = locking_limit_deg(q, MU_GREASED), locking_limit_deg(q, MU_DRY)
    if q['lead_angle_deg'] <= lim_g:
        locking = tr('sí')
    elif q['lead_angle_deg'] <= lim_d:
        locking = tr('solo en seco')
    else:
        locking = tr('no')
    lines = [tr('Relación: %g:1') % round(q['teeth'] / q['starts'], 3),
             tr('Entre ejes: %.2f mm') % q['A'],
             tr('Avance: %.3f mm') % q['lead'],
             tr('Hélice: %.2f° a %s') % (q['lead_angle_deg'], tr('izquierdas') if q['hand'] < 0 else tr('derechas')),
             tr('Rendimiento: %.0f %% con grasa, %.0f %% en seco') % (100 * eta_g, 100 * eta_d),
             tr('Autobloqueo: %s') % locking,
             tr('Sinfín: Ø%.2f, fondo Ø%.2f') % (2 * q['r_tip'], 2 * q['r_root']),
             tr('Rueda: Ø%.2f, borde Ø%.2f') % (2 * q['R2'], 2 * q['rim']),
             tr('Cresta del sinfín: %.2f mm') % crest]
    if land is not None:
        lines.append(tr('Cabeza del diente: %.2f mm') % land)
    if partial:
        lines.append(tr('Filete: %.1f mm (mín. %.1f), lisos Ø%.2f') % (2 * q['thread_half'], need, 2 * q['r_shoulder']))
    if q['chamfer_z'] is not None:
        lines.append(tr('Chaflán: desde z = ±%.2f mm') % q['chamfer_z'])
    summary = '\n'.join(lines)
    return q, errors, warns, summary


if __name__ == '__main__':
    for prm in ({}, dict(module=2, teeth=20, starts=2, flank_deg=30, addendum_f=0.8, dedendum_f=1.0,
                         worm_pitch_d=20, wheel_width=12, worm_length=36, rim_over_tip=0.8)):
        q, errs, warns, summ = check_params(prm)
        print(summ)
        print('errores:', errs)
        print('avisos:', warns)
        for c in (q['section_z'][0], 0.0, q['section_z'][-1]):
            l, r, rr, ro = gap_profile(q, c)
            print('  c=%+.2f fondo %.3f  izq %.2f°→%.2f°  der %.2f°→%.2f°' % (
                c, rr, math.degrees(angle_from_y(l[0])), math.degrees(angle_from_y(l[-1])),
                math.degrees(angle_from_y(r[0])), math.degrees(angle_from_y(r[-1]))))
    # a izquierdas: el hueco tiene que ser el simétrico exacto del de a derechas
    qr, ql = derive({}), derive(dict(left_handed=True))
    for c in qr['section_z']:
        lr, rr_, _, _ = gap_profile(qr, c)
        ll, rl, _, _ = gap_profile(ql, c)
        assert all(math.isclose(a[0], -b[0]) and math.isclose(a[1], b[1]) for a, b in zip(ll + rl, rr_ + lr))
    print('a izquierdas: hueco simétrico, bien')
    # rendimiento: el autobloqueo tiene que coincidir con el rendimiento hacia atrás ≤ 0
    q20 = derive(dict(flank_deg=20))
    for q_ in (derive({}), q20, derive(dict(starts=2)), derive(dict(starts=3))):
        for mu in (0.05, MU_GREASED, MU_DRY):
            assert (efficiency(q_, mu)[1] <= 0) == (q_['lead_angle_deg'] <= locking_limit_deg(q_, mu))
    print('rendimiento con μ 0.05 (acero con aceite): %.0f %% con 20° de flanco, %.0f %% con 45°'
          % (100 * efficiency(q20, 0.05)[0], 100 * efficiency(derive({}), 0.05)[0]))
    for shape, size, flat in (('hex', 5.6, 0), ('square', 5, 0), ('d', 5.1, 4.6), ('keyway', 8.1, 0)):
        print('taladro %s %.1f: radio máx. %.2f, %d tramos' % (shape, size, bore_radius(shape, size, flat),
                                                              len(bore_outline(shape, size, flat))))
