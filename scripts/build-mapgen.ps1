[CmdletBinding()]
param()

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$projectRoot = Get-ProjectBroomRoot
$sourceRoot = Join-Path $projectRoot "src\brogue-mapgen"
$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."
$make = Resolve-ProjectBroomMsysTool "make.exe"
$gcc = Resolve-ProjectBroomMsysTool "x86_64-w64-mingw32-gcc.exe"
Enable-ProjectBroomMsysPath @($make, $gcc)
$gccFlavor = Split-Path -Leaf (Split-Path -Parent (Split-Path -Parent $gcc))
$makePath = "PATH=/usr/bin:/$gccFlavor/bin:/bin"

Push-Location $sourceRoot
try {
    & $python "tools\generate_tile_names.py"
    if ($LASTEXITCODE -ne 0) { throw "Tile-name generation failed with exit code $LASTEXITCODE." }

    & $make $makePath SYSTEM=WINDOWS GRAPHICS=NO RELEASE=YES bin/brogue.exe
    if ($LASTEXITCODE -ne 0) { throw "Brogue exporter build failed with exit code $LASTEXITCODE." }
}
finally {
    Pop-Location
}

Write-Output (Join-Path $sourceRoot "bin\brogue.exe")
