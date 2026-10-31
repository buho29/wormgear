# Enlaza la raíz del repo en la carpeta Mod de FreeCAD (junction: no hace falta ser administrador).
# Es lo mismo que hace el gestor de complementos: FreeCAD lee package.xml y carga el banco desde freecad/.
# FreeCAD 1.1 usa %APPDATA%\FreeCAD\v1-1\Mod (una por versión); FreeCAD 1.0, %APPDATA%\FreeCAD\Mod.
# Uso:  powershell -ExecutionPolicy Bypass -File freecad\install.ps1
$base = Join-Path $env:APPDATA 'FreeCAD'
$versioned = Get-ChildItem $base -Directory -Filter 'v*' -ErrorAction SilentlyContinue | Sort-Object Name | Select-Object -Last 1
$mod = if ($versioned) { Join-Path $versioned.FullName 'Mod' } else { Join-Path $base 'Mod' }
$link = Join-Path $mod 'WormGear'
$target = Split-Path $PSScriptRoot -Parent

if (-not (Test-Path $base)) {
    Write-Error "No encuentro la carpeta de usuario de FreeCAD: $base (¿has abierto FreeCAD alguna vez?)"
    exit 1
}
New-Item -ItemType Directory -Force $mod | Out-Null
if (Test-Path $link) {
    $item = Get-Item $link -Force
    if ($item.LinkType -eq 'Junction' -and $item.Target -contains $target) {
        Write-Host "Ya estaba enlazado: $link -> $target"
        exit 0
    }
    Write-Error "Ya existe $link y no es un enlace a este repo; bórralo o renómbralo antes."
    exit 1
}
New-Item -ItemType Junction -Path $link -Target $target | Out-Null
Write-Host "Enlazado: $link -> $target"
Write-Host "Reinicia FreeCAD y elige el banco de trabajo 'Sinfín y rueda'."
