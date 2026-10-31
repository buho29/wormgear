# Registra esta carpeta del repo en la lista de complementos de Fusion 360 con su ruta real, como el botón "+" del
# diálogo de complementos, y con "Ejecutar al inicio". Fusion carga directamente lo que hay en el repo.
# No se usa un enlace (junction) en la carpeta AddIns: Fusion lo sigue hasta aquí y el complemento sale dos veces.
# Hay que cerrar Fusion antes: guarda su lista al salir y pisaría el cambio.
# Uso:  powershell -ExecutionPolicy Bypass -File fusion\install.ps1
$fusionDir = Join-Path $env:APPDATA 'Autodesk\Autodesk Fusion 360'
$link = Join-Path $fusionDir 'API\AddIns\WormGear'
$script = (Join-Path $PSScriptRoot 'WormGear.py') -replace '\\', '/'
$oldLink = '/API/AddIns/WormGear/WormGear.py'

if (Get-Process Fusion360 -ErrorAction SilentlyContinue) {
    Write-Error 'Cierra Fusion antes de ejecutar este script.'
    exit 1
}

# El enlace de instalaciones anteriores (rmdir quita solo el enlace, no la carpeta del repo)
if (Test-Path $link) {
    $item = Get-Item $link -Force
    if ($item.LinkType -eq 'Junction') {
        cmd /c rmdir "$link"
        Write-Host "Quitado el enlace antiguo: $link"
    } else {
        Write-Warning "$link es una instalación copiada (instalar.bat). Quítala con desinstalar.bat o saldrá dos veces."
    }
}

# La lista de complementos está en una carpeta por usuario de Autodesk
$lists = @(Get-ChildItem $fusionDir -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName 'JSLoadedScriptsinfo' } | Where-Object { Test-Path $_ })
if (-not $lists) {
    Write-Error "No encuentro la lista de complementos de Fusion en $fusionDir. Abre Fusion una vez, ciérralo y repite."
    exit 1
}

foreach ($list in $lists) {
    Copy-Item $list "$list.bak" -Force
    $data = Get-Content $list -Raw -Encoding UTF8 | ConvertFrom-Json
    $old = @($data.loadedScripts | Where-Object { $_.path -eq $script })
    $data.loadedScripts = @($data.loadedScripts | Where-Object { $_.path -ne $script -and -not $_.path.EndsWith($oldLink) }) + [pscustomobject]@{
        name = 'WormGear'
        path = $script
        location = 3
        isRemoved = $false
        isFavorite = [bool]($old | Where-Object { $_.isFavorite })
        runOnStartup = $true
    }
    [IO.File]::WriteAllText($list, ($data | ConvertTo-Json -Depth 5))
    Write-Host "Registrado en $list -> $script (copia en $list.bak)"
}
Write-Host 'Al abrir Fusion, WormGear arranca solo. Para pararlo o quitarlo: Utilidades > Complementos (Mayús+S).'
