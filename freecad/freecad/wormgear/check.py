# Comprobación del engrane con copias de los sólidos (no toca el documento), como en el add-in de Fusion:
# - interferencia sinfín/rueda en varias fases de un paso de diente, en todo el ancho de la rueda;
# - juego: cuánto gira el sinfín, con la rueda quieta, hasta tocar por cada lado.
# Los sólidos van en el marco de shapes.py (sinfín en su sitio, rueda en el origen).
import math

import FreeCAD as App
import Part

V = App.Vector
TOL = 1e-4   # mm³: por debajo se considera que no tocan
BISECT = 10  # pasos de la bisección del juego (precisión ≈ 0.02°)


def check(q, worm_shape, wheel_shape, phases=8, progress=None):
    """progress(hecho, total), si se da, se llama tras cada medida (cada una tarda unos segundos)."""
    total = phases + 2 * (BISECT + 1)
    done = [0]
    # solo la zona de la rueda que puede tocar el sinfín, para que sea rápido
    # (medidas con decimales raros para que ninguna cara de la caja coincida con otra)
    y0 = q['A'] - q['hob_tip'] - 1.5
    y1 = q['rim'] + 1.0
    lx, lz = q['worm_length'] + 4.03, q['wheel_width'] + 2.07
    zone = Part.makeBox(lx, y1 - y0, lz, V(0.013 - lx / 2, y0, 0.011 - lz / 2)).common(wheel_shape)
    axis_c, axis_d = V(0, q['A'], 0), V(1, 0, 0)

    def overlap(theta, dphi=0.0):
        # si OCCT no sabe cortar (contacto casi tangente), se repite con un giro mínimo
        for eps in (0.0, 1e-6, -1e-6, 1e-5, -1e-5):
            w = worm_shape.copy()
            w.rotate(axis_c, axis_d, math.degrees((theta + eps) * q['teeth'] / q['starts'] + dphi))
            w.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(theta + eps))
            try:
                v = zone.common(w).Volume
            except Exception:
                continue
            break
        else:
            v = float('inf')   # no se puede medir: se cuenta como contacto
        done[0] += 1
        if progress:
            progress(done[0], total)
        return v

    pitch = 2 * math.pi / q['teeth']
    vols = [overlap(pitch * k / phases) for k in range(phases)]

    def first_contact(sign):
        hi = math.radians(2 * 360 * q['backlash'] / q['lead'] + 2)
        if overlap(0, sign * hi) <= TOL:
            return None
        lo = 0.0
        for _ in range(BISECT):
            mid = (lo + hi) / 2
            if overlap(0, sign * mid) > TOL:
                hi = mid
            else:
                lo = mid
        return math.degrees((lo + hi) / 2)

    pos, neg = first_contact(+1), first_contact(-1)
    play_mm = None if pos is None or neg is None else (pos + neg) / 360 * q['lead']
    return dict(overlaps=vols, max_overlap=max(vols), play_pos_deg=pos, play_neg_deg=neg, play_mm=play_mm)


def report(res, q):
    ok = res['max_overlap'] <= TOL
    lines = ['Interferencia en %d fases de un diente: %s (máx. %.4f mm³)'
             % (len(res['overlaps']), 'ninguna' if ok else 'SÍ', res['max_overlap'])]
    if res['play_mm'] is None:
        lines.append('Juego: no he encontrado contacto girando el sinfín (¿demasiada holgura?).')
    else:
        lines.append('Juego: el sinfín gira +%.2f° / -%.2f° hasta tocar = %.3f mm axiales (pedido %.3f mm)'
                     % (res['play_pos_deg'], res['play_neg_deg'], res['play_mm'], q['backlash']))
    return ok, '\n'.join(lines)
