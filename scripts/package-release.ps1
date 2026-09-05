[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidatePattern('^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')][string]$Version,
    [switch]$SkipBuild
)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."
$output = Join-Path $root "artifacts\release\$Version"
$venv = Join-Path $root ".build\packaging-venv"
$mapcompilerDist = Join-Path $root ".build\mapcompiler"

if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot "bootstrap-dev.ps1")
    & (Join-Path $PSScriptRoot "build-dev.ps1")
}

if (-not (Test-Path -LiteralPath (Join-Path $venv "Scripts\python.exe") -PathType Leaf)) {
    & $python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create packaging environment." }
}
$venvPython = Join-Path $venv "Scripts\python.exe"
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $root "tools\packaging\requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Could not install pinned packaging dependencies." }

& $venvPython -m PyInstaller --noconfirm --clean --distpath $mapcompilerDist --workpath (Join-Path $root ".build\pyinstaller") (Join-Path $root "tools\packaging\ProjectBroomMapCompiler.spec")
if ($LASTEXITCODE -ne 0) { throw "Map compiler packaging failed." }

& (Join-Path $PSScriptRoot "build-launcher.ps1") -SelfContained -OutputDirectory ".build\launcher"

$engineDir = Join-Path $root ".build\uzdoom"
$launcher = Join-Path $root ".build\launcher\ProjectBroom.exe"
$mapcompiler = Join-Path $mapcompilerDist "ProjectBroomMapCompiler.exe"
New-Item -ItemType Directory -Force -Path $output | Out-Null

& $python (Join-Path $root "tools\packaging\package_release.py") --root $root --version $Version --engine-dir $engineDir --launcher $launcher --mapcompiler $mapcompiler --output $output
if ($LASTEXITCODE -ne 0) { throw "Release assembly failed." }

& (Join-Path $PSScriptRoot "verify-release.ps1") -ReleaseDirectory $output
Write-Output $output
