[CmdletBinding()]
param([switch]$SkipTests)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$engineBuild = Join-Path $root ".build\uzdoom"

if (-not (Test-Path -LiteralPath (Join-Path $engineBuild "CMakeCache.txt") -PathType Leaf)) {
    & (Join-Path $PSScriptRoot "bootstrap-dev.ps1")
}

$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."
Invoke-ProjectBroomCommand $python -Arguments @((Join-Path $root "tools\engine_source.py"), "--root", $root)

& (Join-Path $PSScriptRoot "build-bridge.ps1")
& (Join-Path $PSScriptRoot "build-mapgen.ps1")

$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."
Invoke-ProjectBroomCommand $python -Arguments @((Join-Path $root "tools\monster_models\generate.py"))
Push-Location $root
try { Invoke-ProjectBroomCommand $python -Arguments @((Join-Path $root "tools\weapon_models\generate.py")) }
finally { Pop-Location }

if (-not $SkipTests) {
    & (Join-Path $PSScriptRoot "test.ps1") -Quick
}

$cmake = Resolve-ProjectBroomCommand "cmake.exe" "Install CMake."
Invoke-ProjectBroomCommand $cmake -Arguments @("--build", $engineBuild, "--config", "Release", "-j", "4")

Copy-ProjectBroomEngineRuntime
Invoke-ProjectBroomCommand $python -Arguments @((Join-Path $root "tools\engine_source.py"), "--root", $root, "--record-build", (Get-ProjectBroomEngineDirectory))

& (Join-Path $PSScriptRoot "build-launcher.ps1") -SelfContained

Write-Output (Join-Path $engineBuild "Release\uzdoom.exe")
if (-not (Test-Path -LiteralPath (Join-Path $engineBuild "Release\uzdoom.exe"))) {
    Write-Output (Join-Path $engineBuild "uzdoom.exe")
}
