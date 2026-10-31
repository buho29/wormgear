@echo off
rem Quita el add-in WormGear (Sinfín y rueda) de la carpeta de complementos de Fusion 360.
chcp 65001 >nul
setlocal
set "ADDINS=%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns"
set "DST=%ADDINS%\WormGear"

if not exist "%DST%" (
    echo WormGear no está instalado en %ADDINS%.
    echo WormGear is not installed in %ADDINS%.
    goto :fin
)
rem Un enlace al repo (instalación de desarrollo) no se borra desde aquí
dir /AL /B "%ADDINS%" 2>nul | findstr /X /I "WormGear" >nul
if not errorlevel 1 (
    echo %DST% es un enlace a otra carpeta, no lo borro.
    echo %DST% is a link to another folder, not deleting it.
    goto :fin
)

echo Antes de seguir, detén el complemento en Fusion (Utilidades ^> Complementos ^> WormGear ^> Detener)
echo o cierra Fusion.
echo First stop the add-in in Fusion (Utilities ^> Add-Ins ^> WormGear ^> Stop) or close Fusion.
pause
rmdir /S /Q "%DST%"
if exist "%DST%" (
    echo No se ha podido borrar del todo %DST%. Cierra Fusion y vuelve a probar.
    echo %DST% could not be fully deleted. Close Fusion and try again.
) else (
    echo WormGear desinstalado. / WormGear uninstalled.
)

:fin
echo.
pause
