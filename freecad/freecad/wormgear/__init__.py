# Banco de trabajo "Sinfín y rueda" de FreeCAD (ver README.md).
# Al importar el paquete se elige el idioma de los textos: castellano si FreeCAD lo está; si no, inglés.
from . import i18n


def _language():
    """Idioma de FreeCAD: el elegido en las preferencias ('Spanish', 'English'…) o, si no hay, el del sistema
    ('es_ES'…), que es el que usa FreeCAD entonces. Al arrancar, FreeCADGui aún no tiene getLocale()."""
    import FreeCAD as App
    name = App.ParamGet('User parameter:BaseApp/Preferences/General').GetString('Language')
    if name:
        return name
    try:
        from PySide import QtCore
        return QtCore.QLocale.system().name()
    except Exception:
        import locale
        return locale.getlocale()[0] or ''


i18n.set_language(_language())
