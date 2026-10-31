# Lo carga FreeCAD al arrancar la interfaz: registra el banco de trabajo "Sinfín y rueda".
import os

import FreeCADGui as Gui

ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '64x64.png')


class WormGearWorkbench(Gui.Workbench):
    MenuText = 'Sinfín y rueda'
    ToolTip = 'Sinfín y rueda lisa paramétricos, para imprimir en 3D'
    Icon = ICON

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        from freecad.wormgear import commands
        names = commands.register()
        self.appendToolbar('Sinfín y rueda', names)
        self.appendMenu('Sinfín y rueda', names)

    def Activated(self):
        pass

    def Deactivated(self):
        pass


Gui.addWorkbench(WormGearWorkbench())
