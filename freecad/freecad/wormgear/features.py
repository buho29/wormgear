# Objetos paramétricos del banco "Sinfín y rueda".
# - WormGearPair ("Sinfín y rueda"): guarda todos los parámetros y genera los dos sólidos (compound: sinfín,
#   rueda). Va oculto: es el que se edita.
# - WormGearPart ("Sinfín" / "Rueda"): cada pieza por separado, sacada del compound, para verla, moverla y
#   exportar su STL.
# Los nombres de las propiedades van en inglés (son identificadores) y la descripción, en castellano.
import os

import FreeCAD as App

from . import geometry as G

HERE = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(HERE, 'resources', '64x64.png')

# (propiedad, clave de geometry, tipo, grupo, descripción, (mín, máx, paso) para los enteros y factores)
PROPS = [
    ('Module', 'module', 'App::PropertyLength', 'Engrane', 'Módulo axial del sinfín (mm)'),
    ('Starts', 'starts', 'App::PropertyIntegerConstraint', 'Engrane', 'Entradas del sinfín', (1, 4, 1)),
    ('Teeth', 'teeth', 'App::PropertyIntegerConstraint', 'Engrane', 'Dientes de la rueda', (3, 300, 1)),
    ('WormPitchDiameter', 'worm_pitch_d', 'App::PropertyLength', 'Engrane', 'Diámetro primitivo del sinfín'),
    ('FlankAngle', 'flank_deg', 'App::PropertyAngle', 'Engrane',
     'Ángulo de flanco en la sección axial (45° = sin voladizos con el sinfín de pie)'),
    ('AddendumFactor', 'addendum_f', 'App::PropertyFloatConstraint', 'Engrane', 'Cabeza del filete (× módulo)', (0.1, 1.5, 0.05)),
    ('DedendumFactor', 'dedendum_f', 'App::PropertyFloatConstraint', 'Engrane', 'Pie del filete (× módulo)', (0.1, 1.5, 0.05)),
    ('Clearance', 'clearance', 'App::PropertyLength', 'Engrane', 'Holgura radial entre la cabeza y el fondo'),
    ('Backlash', 'backlash', 'App::PropertyLength', 'Engrane', 'Holgura entre flancos, medida en el eje del sinfín'),
    ('WormLength', 'worm_length', 'App::PropertyLength', 'Sinfín', 'Longitud del sinfín'),
    ('WormBore', 'worm_bore', 'App::PropertyLength', 'Sinfín', 'Diámetro del taladro del sinfín (0 = sin taladro)'),
    ('WheelWidth', 'wheel_width', 'App::PropertyLength', 'Rueda', 'Ancho de la rueda'),
    ('WheelBore', 'wheel_bore', 'App::PropertyLength', 'Rueda', 'Diámetro del taladro de la rueda (0 = sin taladro)'),
    ('RimOverTip', 'rim_over_tip', 'App::PropertyLength', 'Rueda',
     'Cuánto sobresale el borde de la rueda por encima de la cabeza de sus dientes en el plano medio'),
    ('Sections', 'sections', 'App::PropertyIntegerConstraint', 'Rueda', 'Perfiles de la solevación del hueco', (5, 81, 2)),
]
WORM_ONLY = ('worm_length', 'worm_bore')                                  # no cambian la rueda
WHEEL_ONLY = ('wheel_width', 'wheel_bore', 'rim_over_tip', 'sections')   # no cambian el sinfín


def params(obj):
    """Parámetros de geometry (mm, grados) leídos de las propiedades del objeto."""
    prm = {}
    for p in PROPS:
        name, key, kind = p[0], p[1], p[2]
        v = getattr(obj, name)
        prm[key] = v.Value if hasattr(v, 'Value') else v
    return prm


class WormGearPair:
    def __init__(self, obj):
        for p in PROPS:
            name, key, kind, group, doc = p[:5]
            obj.addProperty(kind, name, group, doc)
            v = G.DEFAULTS[key]
            if kind in ('App::PropertyIntegerConstraint', 'App::PropertyFloatConstraint'):
                setattr(obj, name, (v,) + tuple(p[5]))
            else:
                setattr(obj, name, v)
        obj.addProperty('App::PropertyString', 'Summary', 'Resultado', 'Relación, distancia entre ejes, diámetros…')
        obj.addProperty('App::PropertyStringList', 'Warnings', 'Resultado', 'Avisos de la última generación')
        obj.addProperty('App::PropertyLength', 'CenterDistance', 'Resultado', 'Distancia entre ejes')
        for name in ('Summary', 'Warnings', 'CenterDistance'):
            obj.setEditorMode(name, 1)   # solo lectura
        obj.setEditorMode('Placement', 2)   # oculto: lo que se mueve son las piezas
        obj.Proxy = self
        self._cache = {}

    def execute(self, obj):
        from . import shapes as S   # Part solo hace falta al generar
        import Part
        prm = params(obj)
        q, errors, warns, summary = G.check_params(prm)
        obj.Summary = summary.replace('\n', ' · ')
        obj.Warnings = warns
        obj.CenterDistance = q['A']
        if errors:
            raise ValueError(' '.join(errors))
        for w in warns:
            App.Console.PrintWarning('%s: %s\n' % (obj.Label, w))
        # la rueda tarda; si solo ha cambiado el sinfín se reutiliza la anterior (y al revés)
        cache = getattr(self, '_cache', None)
        if cache is None:
            cache = self._cache = {}
        worm_key = tuple(sorted((k, v) for k, v in prm.items() if k not in WHEEL_ONLY))
        wheel_key = tuple(sorted((k, v) for k, v in prm.items() if k not in WORM_ONLY))
        worm = cache.get(('worm', worm_key))
        if worm is None:
            worm = S.worm_shape(q)
        wheel = cache.get(('wheel', wheel_key))
        if wheel is None:
            wheel = S.wheel_shape(q)
        self._cache = {('worm', worm_key): worm, ('wheel', wheel_key): wheel}
        # sin Placement propio: la posición de cada pieza va en su objeto (WormGearPart)
        obj.Shape = Part.makeCompound([worm, wheel])

    def onDocumentRestored(self, obj):
        self._cache = {}

    def dumps(self):
        return None

    def loads(self, state):
        self._cache = {}

    __getstate__ = dumps
    __setstate__ = loads


class WormGearPart:
    """Una de las dos piezas (Index 0 = sinfín, 1 = rueda) del compound de un WormGearPair."""

    def __init__(self, obj, pair, index):
        obj.addProperty('App::PropertyLink', 'Pair', 'Sinfín y rueda', 'Objeto con los parámetros')
        obj.addProperty('App::PropertyInteger', 'Index', 'Sinfín y rueda', '0 = sinfín, 1 = rueda')
        obj.Pair = pair
        obj.Index = index
        obj.setEditorMode('Index', 2)   # oculto
        obj.Proxy = self

    def execute(self, obj):
        solids = obj.Pair.Shape.Solids if obj.Pair else []
        if len(solids) != 2:
            raise ValueError('"%s" no tiene los dos sólidos.' % (obj.Pair.Label if obj.Pair else '?'))
        shape = solids[obj.Index].copy()
        shape.Placement = obj.Placement   # los sólidos vienen sin Placement: así se conserva si se mueve la pieza
        obj.Shape = shape

    def dumps(self):
        return None

    def loads(self, state):
        pass

    __getstate__ = dumps
    __setstate__ = loads


class ViewProviderPair:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.Object = vobj.Object

    def getIcon(self):
        return ICON

    def claimChildren(self):
        return list(getattr(self.Object, 'InList', []))

    def dumps(self):
        return None

    def loads(self, state):
        pass

    __getstate__ = dumps
    __setstate__ = loads


class ViewProviderPart(ViewProviderPair):
    def claimChildren(self):
        return []


def create(doc=None, prm=None):
    """Crea el objeto con los parámetros y sus dos piezas. Devuelve (pair, worm, wheel)."""
    doc = doc or App.ActiveDocument or App.newDocument()
    pair = doc.addObject('Part::FeaturePython', 'WormGearPair')
    WormGearPair(pair)
    for p in PROPS:
        if prm and p[1] in prm:
            v = prm[p[1]]
            setattr(pair, p[0], int(v) if p[2] == 'App::PropertyIntegerConstraint' else v)
    parts = []
    for index, label in ((0, 'Sinfín'), (1, 'Rueda')):
        o = doc.addObject('Part::FeaturePython', 'WormGearWorm' if index == 0 else 'WormGearWheel')
        WormGearPart(o, pair, index)
        o.Label = label
        parts.append(o)
    if App.GuiUp:
        ViewProviderPair(pair.ViewObject)
        pair.ViewObject.Visibility = False
        for o in parts:
            ViewProviderPart(o.ViewObject)
    pair.Label = 'Sinfín y rueda m%g %d-%d' % (pair.Module.Value, pair.Teeth, pair.Starts)
    return pair, parts[0], parts[1]
