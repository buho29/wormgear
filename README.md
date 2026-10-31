# WormGear: sinfín y rueda para imprimir en 3D

Genera un tornillo sin fin y su rueda dentada, paramétricos y pensados para imprimir sin soportes. La rueda no se dibuja a ojo: sus dientes se tallan con la envolvente exacta del sinfín, así que salen lisos (unas 6 caras por diente) y no interfieren.

![Sinfín y rueda girando](fusion/img/engrane.gif)

Hay dos versiones, con la misma matemática (`wormgear/geometry.py`, copiada en las dos):

| | Qué es | Instalación |
|---|---|---|
| [**Fusion 360**](fusion/README.md) | Add-in con diálogo. En ensamblajes crea juntas de giro y un enlace de movimiento con la relación. | Zip de las [Releases](https://github.com/buho29/wormgear/releases) con `instalar.bat`. |
| [**FreeCAD**](freecad/README.md) | Banco de trabajo con objetos paramétricos: cambias una propiedad y se recalcula. | Gestor de complementos (repositorio personalizado) o copia en `Mod`. |

Las dos traen:
- un chaflán automático de 45° en las caras de la rueda;
- avisos de voladizos, crestas finas, dientes en punta y poco cubo;
- una comprobación que mide la interferencia en 8 posiciones y el juego real entre flancos.

Los valores por defecto (flanco de 45° y diente bajo) están pensados para imprimir el sinfín de pie y la rueda tumbada sin soportes.

Cómo se calcula la rueda, con diagramas: [fusion/README.md](fusion/README.md#cómo-se-calcula-la-rueda).

## Licencia

[MIT](LICENSE).
