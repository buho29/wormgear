# Textos en inglés. Los textos del código están en castellano y sirven de clave: tr(texto) devuelve la
# traducción si el CAD no está en castellano. Sin dependencias de ningún CAD (lo usa geometry.py).
# Es igual en Fusion y en FreeCAD: si se cambia uno, hay que copiarlo al otro (las pruebas lo comprueban).
# Al añadir un texto con tr(), añade aquí su traducción, con los mismos % en el mismo orden.

LANG = 'es'


def set_language(name):
    """'es', 'es-ES', 'Spanish'… -> castellano; cualquier otro idioma -> inglés."""
    global LANG
    LANG = 'es' if name.lower().startswith(('es', 'spanish')) else 'en'


def tr(text):
    return text if LANG == 'es' else EN.get(text, text)


def labels_of(text):
    """El texto en todos los idiomas (para reconocer valores guardados en otro idioma)."""
    return [text, EN.get(text, text)]


EN = {
    # ------------------------------------------------ nombres y diálogo
    'Sinfín y rueda': 'Worm and wheel',
    'Sinfín': 'Worm',
    'Rueda': 'Wheel',
    'Engrane': 'Gear',
    'Resumen': 'Summary',
    'Opciones': 'Options',
    'Generar': 'Generate',
    'Solo el sinfín': 'Worm only',
    'Solo la rueda': 'Wheel only',
    'Comprobar engrane': 'Check mesh',
    'Comprobar engrane al terminar': 'Check mesh when done',
    'Módulo': 'Module',
    'Entradas del sinfín': 'Worm starts',
    'Dientes de la rueda': 'Wheel teeth',
    'Ø primitivo del sinfín': 'Worm pitch Ø',
    'Ángulo de flanco': 'Flank angle',
    'Cabeza (× módulo)': 'Addendum (× module)',
    'Pie (× módulo)': 'Dedendum (× module)',
    'Holgura radial': 'Radial clearance',
    'Holgura entre flancos': 'Backlash',
    'A izquierdas': 'Left-handed',
    'Longitud': 'Length',
    'Longitud con filete (0 = todo)': 'Threaded length (0 = all)',
    'Ø tramos lisos (0 = auto)': 'Plain ends Ø (0 = auto)',
    'Taladro': 'Bore',
    'Ø o entre caras (0 = sin taladro)': 'Ø or across flats (0 = no bore)',
    'Plano en D (al lado opuesto)': 'D flat (to the opposite side)',
    'Ancho': 'Width',
    'Borde sobre la cabeza': 'Rim over tip',
    'Perfiles de la solevación': 'Loft sections',
    'Redondo': 'Round',
    'Plano en D': 'D flat',
    'Hexagonal': 'Hexagonal',
    'Cuadrado': 'Square',
    'Chavetero DIN 6885': 'DIN 6885 keyway',
    'Sinfín y su rueda dentada, paramétricos e imprimibles. La rueda se genera con perfiles de envolvente '
    'calculados y una solevación (dientes lisos, sin interferencias).':
        'Parametric, printable worm and worm wheel. The wheel is a loft of computed envelope profiles '
        '(smooth teeth, no interference).',
    '<b><font color="#d33">✖ No entiendo el valor de: %s.</font></b><br>Escribe un número con punto decimal y, '
    'si quieres, la unidad (p. ej. <i>1.5 mm</i>, <i>45 deg</i>).':
        '<b><font color="#d33">✖ Cannot read the value of: %s.</font></b><br>Type a number with a decimal point '
        'and, optionally, the unit (e.g. <i>1.5 mm</i>, <i>45 deg</i>).',
    '<b><font color="#d33">✖ Con estos valores no sale geometría: %s</font></b>':
        '<b><font color="#d33">✖ These values give no geometry: %s</font></b>',
    '<b><font color="#d33">✖ Error interno del complemento:</font></b><br>%s':
        '<b><font color="#d33">✖ Internal add-in error:</font></b><br>%s',
    'Abre un diseño (espacio de trabajo DISEÑO) antes de usar Sinfín y rueda.':
        'Open a design (DESIGN workspace) before using Worm and wheel.',
    'No se pudo generar: %s': 'Could not generate: %s',
    'Sinfín y rueda: error': 'Worm and wheel: error',
    'Sinfín y rueda: error al arrancar': 'Worm and wheel: error on start',
    'Sinfín y rueda: error al parar': 'Worm and wheel: error on stop',
    'Sinfín y rueda: error al abrir el diálogo': 'Worm and wheel: error opening the dialog',

    # ------------------------------------------------ línea de tiempo de Fusion
    'Rueda en bruto': 'Wheel blank',
    'Hueco z=%+.2f': 'Gap z=%+.2f',
    'Hueco del diente': 'Tooth gap',
    'Huecos': 'Gaps',
    'Tallar rueda': 'Cut wheel',
    'Taladro del sinfín': 'Worm bore',
    'Taladro de la rueda': 'Wheel bore',
    'Eje rueda': 'Wheel axis',
    'Eje sinfín': 'Worm axis',
    'Ejes %s': 'Axes %s',
    'Giro rueda': 'Wheel rotation',
    'Giro sinfín': 'Worm rotation',
    'Sinfín %s': 'Worm %s',
    'Rueda %s': 'Wheel %s',
    'Sinfín y rueda %s': 'Worm and wheel %s',
    ' izq': ' LH',
    'rueda': 'wheel',
    'sinfín': 'worm',
    'Sinfín: %d caras, %.0f mm³': 'Worm: %d faces, %.0f mm³',
    'Rueda: %d caras (%.1f por diente), %.0f mm³': 'Wheel: %d faces (%.1f per tooth), %.0f mm³',
    'Diseño de pieza: sinfín y rueda van como cuerpos (sin componentes ni juntas).':
        'Part design: worm and wheel are bodies (no components or joints).',
    'El contorno de "%s" no ha salido cerrado (%d perfiles).': 'The outline of "%s" is not closed (%d profiles).',
    'El perfil del hueco en z=%.2f no ha salido cerrado (%d perfiles).':
        'The gap profile at z=%.2f is not closed (%d profiles).',
    '%s: no se pudo crear la junta de giro (%s).': '%s: could not create the revolute joint (%s).',
    'Juntas de giro y enlace de movimiento creados: arrastra el sinfín y gira la rueda.':
        'Revolute joints and motion link created: drag the worm and the wheel turns.',
    'No se pudo crear el enlace de movimiento (%s): créalo a mano, 360° del sinfín = %.4f° de la rueda.':
        'Could not create the motion link (%s): create it by hand, 360° of the worm = %.4f° of the wheel.',
    'No se pudo agrupar la línea de tiempo (%s).': 'Could not group the timeline (%s).',

    # ------------------------------------------------ ventana de progreso de Fusion
    'Generando…': 'Generating…',
    'Sinfín: dibujando la hélice (1 de 2)…': 'Worm: drawing the helix (1 of 2)…',
    'Sinfín: dibujando la hélice (2 de 2)…': 'Worm: drawing the helix (2 of 2)…',
    'Sinfín: barriendo el filete…': 'Worm: sweeping the thread…',
    'Sinfín: uniendo el filete al núcleo…': 'Worm: joining the thread to the core…',
    'Sinfín: recortando la silueta…': 'Worm: trimming the outline…',
    'Sinfín: creando el cuerpo…': 'Worm: creating the body…',
    'Sinfín: haciendo el taladro…': 'Worm: making the bore…',
    'Rueda: preparando el disco…': 'Wheel: preparing the blank…',
    'Rueda: perfil %d de %d…': 'Wheel: section %d of %d…',
    'Rueda: solevando dientes…': 'Wheel: lofting the teeth…',
    'Rueda: repitiendo los huecos…': 'Wheel: patterning the gaps…',
    'Rueda: tallando los dientes…': 'Wheel: cutting the teeth…',
    'Rueda: haciendo el taladro…': 'Wheel: making the bore…',
    'Creando las juntas…': 'Creating the joints…',
    'Terminando…': 'Finishing…',
    'Comprobando interferencias: preparando…': 'Checking interference: preparing…',
    'Comprobando interferencias: fase %d de %d…': 'Checking interference: phase %d of %d…',
    'Comprobando el juego…': 'Checking the backlash…',

    # ------------------------------------------------ comprobación
    'Interferencia en %d fases de un diente: %s (máx. %.4f mm³)':
        'Interference at %d phases of one tooth: %s (max. %.4f mm³)',
    'ninguna': 'none',
    'SÍ': 'YES',
    'Juego: no he encontrado contacto girando el sinfín (¿demasiada holgura?).':
        'Backlash: no contact found turning the worm (too much clearance?).',
    'Juego: el sinfín gira +%.2f° / -%.2f° hasta tocar = %.3f mm axiales (pedido %.3f mm)':
        'Backlash: the worm turns +%.2f° / -%.2f° until contact = %.3f mm axial (requested %.3f mm)',

    # ------------------------------------------------ geometry: resumen, errores y avisos
    'Relación: %g:1': 'Ratio: %g:1',
    'Entre ejes: %.2f mm': 'Center distance: %.2f mm',
    'Avance: %.3f mm': 'Lead: %.3f mm',
    'Hélice: %.2f° a %s': 'Lead angle: %.2f°, %s',
    'derechas': 'right-handed',
    'izquierdas': 'left-handed',
    'Rendimiento: %.0f %% con grasa, %.0f %% en seco': 'Efficiency: %.0f %% greased, %.0f %% dry',
    'Autobloqueo: %s': 'Self-locking: %s',
    'sí': 'yes',
    'solo en seco': 'dry only',
    'no': 'no',
    'Sinfín: Ø%.2f, fondo Ø%.2f': 'Worm: Ø%.2f, root Ø%.2f',
    'Rueda: Ø%.2f, borde Ø%.2f': 'Wheel: Ø%.2f, rim Ø%.2f',
    'Cresta del sinfín: %.2f mm': 'Worm crest: %.2f mm',
    'Cabeza del diente: %.2f mm': 'Tooth tip: %.2f mm',
    'Filete: %.1f mm (mín. %.1f), lisos Ø%.2f': 'Thread: %.1f mm (min. %.1f), plain Ø%.2f',
    'Chaflán: desde z = ±%.2f mm': 'Chamfer: from z = ±%.2f mm',
    'no se pudo calcular el flanco en z=%.2f': 'could not compute the flank at z=%.2f',
    'forma de taladro desconocida (%s)': 'unknown bore shape (%s)',
    'el plano en D tiene que estar entre %.2f y %.2f mm del lado opuesto':
        'the D flat must be between %.2f and %.2f mm from the opposite side',
    'el chavetero DIN 6885 va de Ø6 a Ø65': 'the DIN 6885 keyway covers Ø6 to Ø65',
    'el chavetero es más ancho que el taladro': 'the keyway is wider than the bore',
    'Entradas ≥ 1 y dientes ≥ 3.': 'Starts ≥ 1 and teeth ≥ 3.',
    'El taladro del sinfín no cabe: pared de %.2f mm bajo el fondo del filete.':
        'The worm bore does not fit: %.2f mm wall below the thread root.',
    'Los tramos lisos pueden tener como mucho Ø%.2f (el fondo del filete menos %.1f mm).':
        'The plain ends can be at most Ø%.2f (the thread root minus %.1f mm).',
    'El taladro del sinfín no cabe en los tramos lisos: pared de %.2f mm.':
        'The worm bore does not fit in the plain ends: %.2f mm wall.',
    'Los tramos lisos son demasiado cortos para el escalón de 45° hasta Ø%.2f: acorta el filete o alarga el sinfín.':
        'The plain ends are too short for the 45° step down to Ø%.2f: shorten the thread or lengthen the worm.',
    'El filete es demasiado corto para la rueda: tiene que medir al menos %.1f mm.':
        'The thread is too short for the wheel: it must be at least %.1f mm long.',
    'La rueda es demasiado ancha para este sinfín (ancho/2 tiene que ser < %.1f mm).':
        'The wheel is too wide for this worm (width/2 must be < %.1f mm).',
    'El filete del sinfín acaba en punta (cresta %.2f mm): baja la cabeza o el flanco.':
        'The worm thread comes to a point (crest %.2f mm): reduce the addendum or the flank angle.',
    'Cresta del sinfín de %.2f mm (< 0.4).': 'Worm crest of %.2f mm (< 0.4).',
    'El hueco del sinfín se cierra en el fondo: baja el pie o el flanco.':
        'The worm gap closes at the root: reduce the dedendum or the flank angle.',
    'Fondo del hueco del sinfín de %.2f mm.': 'Worm gap root of %.2f mm.',
    'Con el sinfín de pie, la cara de abajo del filete queda a %.0f° de la horizontal '
    '(el umbral de voladizo del laminador; en Cura, %.0f°).':
        'With the worm standing, the underside of the thread is at %.0f° from the horizontal (the slicer overhang threshold; in Cura, %.0f°).',
    'Los dientes no llegan a las caras: el sinfín solo toca la rueda en %.1f mm de ancho '
    '(estrecha la rueda o agranda el sinfín).':
        'The teeth do not reach the faces: the worm only touches %.1f mm of the wheel width '
        '(make the wheel narrower or the worm larger).',
    'La garganta de la rueda pasa de 45° en las caras: estrecha la rueda o agranda el sinfín.':
        'The wheel throat goes past 45° at the faces: make the wheel narrower or the worm larger.',
    'Puede haber socavado en el pie de los dientes de la rueda (pocos dientes para este flanco).':
        'The wheel teeth may be undercut at the root (few teeth for this flank angle).',
    'El taladro de la rueda no cabe: quedan %.2f mm hasta el fondo de los dientes.':
        'The wheel bore does not fit: %.2f mm left to the tooth root.',
    'Queda poco cubo entre el taladro y el fondo de los dientes (%.1f mm).':
        'Thin hub between the bore and the tooth root (%.1f mm).',
    'Los dientes de la rueda quedan en punta en el borde (%.2f mm): baja "borde sobre la cabeza".':
        'The wheel teeth come to a point at the rim (%.2f mm): reduce "rim over tip".',

    # ------------------------------------------------ FreeCAD: banco, comandos y piezas
    'Sinfín y rueda lisa paramétricos, para imprimir en 3D': 'Parametric worm and smooth worm wheel, for 3D printing',
    'Crea un sinfín y su rueda lisa, paramétricos y pensados para imprimir sin soportes.\n'
    'Los parámetros están en el objeto "Sinfín y rueda" (oculto) del árbol.':
        'Creates a parametric worm and its smooth wheel, designed to print without supports.\n'
        'The parameters are in the (hidden) "Worm and wheel" object in the tree.',
    'Mide la interferencia entre el sinfín y la rueda en 8 posiciones de un diente y el juego.\n'
    'Selecciona antes el sinfín, la rueda o el objeto "Sinfín y rueda". Tarda un par de minutos.':
        'Measures the worm/wheel interference at 8 positions of one tooth, and the backlash.\n'
        'Select the worm, the wheel or the "Worm and wheel" object first. Takes a couple of minutes.',
    'Comprobando el engrane…': 'Checking the mesh…',
    'Cancelar': 'Cancel',
    'Primero tiene que generarse bien.': 'It has to generate correctly first.',
    'Generando el sinfín y la rueda (la rueda tarda unos segundos)…':
        'Generating the worm and the wheel (the wheel takes a few seconds)…',
    'Sinfín y rueda m%g %d-%d%s': 'Worm and wheel m%g %d-%d%s',
    '"%s" no tiene los dos sólidos.': '"%s" does not have both solids.',
    'El sinfín': 'The worm',
    'La rueda': 'The wheel',
    'La solevación del hueco del diente no ha salido válida.': 'The tooth gap loft is not valid.',
    'El sinfín ha salido mal (volumen %.0f mm³, tendría que estar entre %.0f y %.0f): '
    'prueba a cambiar un poco la longitud.':
        'The worm came out wrong (volume %.0f mm³, it should be between %.0f and %.0f): '
        'try changing the length slightly.',
    'No se han tallado bien los dientes de la rueda (%d caras): prueba a cambiar un poco el ancho o el número '
    'de perfiles.':
        'The wheel teeth were not cut correctly (%d faces): try changing the width or the number of sections '
        'slightly.',
    '%s ha salido en %d sólidos.': '%s came out as %d solids.',
    '%s no es un sólido válido.': '%s is not a valid solid.',

    # ------------------------------------------------ FreeCAD: propiedades (grupo y descripción)
    'Resultado': 'Result',
    'Módulo axial del sinfín (mm)': 'Axial module of the worm (mm)',
    'Diámetro primitivo del sinfín': 'Worm pitch diameter',
    'Ángulo de flanco en la sección axial (45° = sin voladizos con el sinfín de pie)':
        'Flank angle in the axial section (45° = no overhangs with the worm standing)',
    'Cabeza del filete (× módulo)': 'Thread addendum (× module)',
    'Pie del filete (× módulo)': 'Thread dedendum (× module)',
    'Holgura radial entre la cabeza y el fondo': 'Radial clearance between tip and root',
    'Holgura entre flancos, medida en el eje del sinfín': 'Backlash between flanks, measured along the worm axis',
    'Sinfín a izquierdas (y su rueda)': 'Left-handed worm (and its wheel)',
    'Longitud del sinfín': 'Worm length',
    'Longitud con filete, centrada (0 = todo el sinfín); el resto son tramos lisos':
        'Threaded length, centered (0 = the whole worm); the rest are plain ends',
    'Diámetro de los tramos lisos (0 = el fondo del filete menos 0.6 mm)':
        'Diameter of the plain ends (0 = the thread root minus 0.6 mm)',
    'Forma del taladro del sinfín': 'Worm bore shape',
    'Diámetro del taladro del sinfín, o medida entre caras si es hexagonal o cuadrado (0 = sin taladro)':
        'Worm bore diameter, or across flats if hexagonal or square (0 = no bore)',
    'Taladro con plano en D: distancia del plano al lado opuesto': 'D-flat bore: distance from the flat to the opposite side',
    'Ancho de la rueda': 'Wheel width',
    'Forma del taladro de la rueda': 'Wheel bore shape',
    'Diámetro del taladro de la rueda, o medida entre caras si es hexagonal o cuadrado (0 = sin taladro)':
        'Wheel bore diameter, or across flats if hexagonal or square (0 = no bore)',
    'Cuánto sobresale el borde de la rueda por encima de la cabeza de sus dientes en el plano medio':
        'How far the wheel rim stands above the tooth tips in the mid-plane',
    'Perfiles de la solevación del hueco': 'Sections of the tooth gap loft',
    'Relación, distancia entre ejes, diámetros…': 'Ratio, center distance, diameters…',
    'Avisos de la última generación': 'Warnings from the last generation',
    'Distancia entre ejes': 'Center distance',
    'Objeto con los parámetros': 'Object with the parameters',
    '0 = sinfín, 1 = rueda': '0 = worm, 1 = wheel',
}


def problems():
    """Comprueba que cada texto que pasa por tr() en esta carpeta (y en WormGear.py, en Fusion) tiene
    traducción, con los mismos % en el mismo orden. Devuelve la lista de problemas."""
    import ast
    import os
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    files = [os.path.join(here, f) for f in os.listdir(here) if f.endswith('.py')]
    files += [os.path.join(here, '..', 'WormGear.py')] if os.path.exists(os.path.join(here, '..', 'WormGear.py')) else []
    spec = re.compile(r'%[-+ #0]*[\d.]*[a-z%]')
    missing = []
    for path in files:
        for node in ast.walk(ast.parse(open(path, encoding='utf-8').read())):
            if (isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'tr' and node.args
                    and isinstance(node.args[0], ast.Constant)):
                text = node.args[0].value
                if text not in EN:
                    missing.append('%s: sin traducción: %r' % (os.path.basename(path), text))
                elif spec.findall(text) != spec.findall(EN[text]):
                    missing.append('%s: los %% no coinciden: %r' % (os.path.basename(path), text))
    # textos que pasan por tr() desde tablas: (nombre de la tabla, posiciones de los textos)
    tables = {'FIELDS': None, 'WHAT': (1,), 'BORE_SHAPES': (1,), 'PROPS': (3, 4), 'RESULT_PROPS': (1, 2),
              'PART_PROPS': (1, 2)}
    for path in files:
        for node in ast.parse(open(path, encoding='utf-8').read()).body:
            name = node.targets[0].id if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) else ''
            if name not in tables:
                continue
            rows = ast.literal_eval(node.value)
            if name == 'FIELDS':
                texts = [t for _, title, fields in rows for t in [title] + [f[1] for f in fields]]
            else:
                texts = [row[i] for row in rows for i in tables[name]]
            missing += ['%s: sin traducción en %s: %r' % (os.path.basename(path), name, t) for t in texts if t not in EN]
    for text, en in EN.items():
        if spec.findall(text) != spec.findall(en):
            missing.append('los %% no coinciden: %r' % text)
    return missing


if __name__ == '__main__':
    found = problems()
    print('\n'.join(found) or 'traducciones: %d, todas bien' % len(EN))
    raise SystemExit(1 if found else 0)
