# Lo carga FreeCAD al arrancar la interfaz: registra el banco de trabajo "Sinfín y rueda".
import os

import FreeCADGui as Gui

from freecad.wormgear.i18n import tr

ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '64x64.png')


class WormGearWorkbench(Gui.Workbench):
    MenuText = tr('Sinfín y rueda')
    ToolTip = tr('Sinfín y rueda lisa paramétricos, para imprimir en 3D')
    Icon = ICON

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        from freecad.wormgear import commands
        names = commands.register()
        self.appendToolbar(tr('Sinfín y rueda'), names)
        self.appendMenu(tr('Sinfín y rueda'), names)

    def Activated(self):
        pass

    def Deactivated(self):
        pass


Gui.addWorkbench(WormGearWorkbench())
