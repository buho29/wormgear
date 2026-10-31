# Comandos del banco "Sinfín y rueda": crear la pareja y comprobar el engrane.
import FreeCAD as App
import FreeCADGui as Gui

from . import features as F


def _selected_pair():
    """El WormGearPair de la selección (vale seleccionar él o una de sus piezas)."""
    for obj in Gui.Selection.getSelection():
        if hasattr(obj, 'Pair'):
            obj = obj.Pair
        if obj is not None and isinstance(getattr(obj, 'Proxy', None), F.WormGearPair):
            return obj
    return None


class CreatePair:
    def GetResources(self):
        return {'Pixmap': F.ICON, 'MenuText': 'Sinfín y rueda',
                'ToolTip': 'Crea un sinfín y su rueda lisa, paramétricos y pensados para imprimir sin soportes.\n'
                           'Los parámetros están en el objeto "Sinfín y rueda" (oculto) del árbol.'}

    def IsActive(self):
        return True

    def Activated(self):
        doc = App.ActiveDocument or App.newDocument()
        doc.openTransaction('Sinfín y rueda')
        try:
            pair, worm, wheel = F.create(doc)
            App.Console.PrintMessage('Generando el sinfín y la rueda (la rueda tarda unos segundos)…\n')
            doc.recompute()
        finally:
            doc.commitTransaction()
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(pair)
        Gui.SendMsgToActiveView('ViewFit')
        App.Console.PrintMessage(pair.Summary + '\n')


class CheckMesh:
    def GetResources(self):
        return {'Pixmap': F.ICON, 'MenuText': 'Comprobar engrane',
                'ToolTip': 'Mide la interferencia entre el sinfín y la rueda en 8 posiciones de un diente y el juego.\n'
                           'Selecciona antes el sinfín, la rueda o el objeto "Sinfín y rueda". Tarda un par de minutos.'}

    def IsActive(self):
        return _selected_pair() is not None

    def Activated(self):
        from PySide import QtCore, QtGui
        from . import check as C, geometry as G
        pair = _selected_pair()
        if pair.State and 'Invalid' in pair.State:
            QtGui.QMessageBox.warning(Gui.getMainWindow(), 'Comprobar engrane', 'Primero tiene que generarse bien.')
            return
        q = G.derive(F.params(pair))
        worm, wheel = [s.copy() for s in pair.Shape.Solids]
        for s in (worm, wheel):            # en el marco de shapes.py, aunque se haya movido el objeto
            s.Placement = App.Placement()
        dlg = QtGui.QProgressDialog('Comprobando el engrane…', 'Cancelar', 0, 100, Gui.getMainWindow())
        dlg.setWindowTitle('Comprobar engrane')
        dlg.setWindowModality(QtCore.Qt.WindowModal)
        dlg.setMinimumDuration(0)

        class Cancelled(Exception):
            pass

        def progress(done, total):
            dlg.setValue(int(100 * done / total))
            QtGui.QApplication.processEvents()
            if dlg.wasCanceled():
                raise Cancelled()

        try:
            res = C.check(q, worm, wheel, progress=progress)
        except Cancelled:
            return
        finally:
            dlg.close()
        ok, text = C.report(res, q)
        App.Console.PrintMessage('%s\n%s\n' % (pair.Label, text))
        box = QtGui.QMessageBox.information if ok else QtGui.QMessageBox.warning
        box(Gui.getMainWindow(), 'Comprobar engrane', text)


def register():
    Gui.addCommand('WormGear_Create', CreatePair())
    Gui.addCommand('WormGear_Check', CheckMesh())
    return ['WormGear_Create', 'WormGear_Check']
