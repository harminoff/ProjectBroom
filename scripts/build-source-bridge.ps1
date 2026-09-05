[CmdletBinding()]
param([switch]$SkipTests)

$projectRoot = Split-Path -Parent $PSScriptRoot
$bridgeBuild = Join-Path $PSScriptRoot "build-bridge.ps1"
$monsterGenerator = Join-Path $projectRoot "tools\monster_models\generate.py"
$weaponGenerator = Join-Path $projectRoot "tools\weapon_models\generate.py"
$engineBuild = Join-Path $projectRoot ".build\gzdoom"
$python = (Get-Command python.exe -ErrorAction Stop).Source

if (-not (Test-Path -LiteralPath (Join-Path $engineBuild "CMakeCache.txt") -PathType Leaf)) {
    & (Join-Path $PSScriptRoot "bootstrap-dev.ps1")
}

& $bridgeBuild

& $python $monsterGenerator
if ($LASTEXITCODE -ne 0) { throw "Monster presentation generation failed with exit code $LASTEXITCODE." }

Push-Location $projectRoot
try {
    & $python $weaponGenerator
    if ($LASTEXITCODE -ne 0) { throw "Weapon presentation generation failed with exit code $LASTEXITCODE." }
} finally {
    Pop-Location
}

if (-not $SkipTests) {
    Push-Location $projectRoot
    try {
        & $python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.weapon_models.test_devices
        if ($LASTEXITCODE -ne 0) { throw "Bridge/resource tests failed with exit code $LASTEXITCODE." }
    } finally {
        Pop-Location
    }
}

# Some Windows hosts provide both Path and PATH. MSBuild rejects that process
# dictionary, so normalize it for this child build.
$buildPath = $env:Path
Remove-Item Env:PATH -ErrorAction SilentlyContinue
$env:Path = $buildPath
& cmake.exe --build $engineBuild --config Release -j 4
if ($LASTEXITCODE -ne 0) { throw "GZDoom source build failed with exit code $LASTEXITCODE." }

$releaseEngine = Join-Path $engineBuild "Release\gzdoom.exe"
$engine = if (Test-Path -LiteralPath $releaseEngine -PathType Leaf) {
    $releaseEngine
} else {
    Join-Path $engineBuild "gzdoom.exe"
}
if (-not (Test-Path -LiteralPath $engine -PathType Leaf)) {
    throw "Expected source-built engine was not produced: $engine"
}
$engineDir = Split-Path -Parent $engine
$runtimeDir = Join-Path $projectRoot ".deps\gzdoom-runtime-4.14.2"
foreach ($runtimeDll in @("openal32.dll", "sndfile.dll", "zmusic.dll")) {
    $runtimeSource = Join-Path $runtimeDir $runtimeDll
    if (-not (Test-Path -LiteralPath $runtimeSource -PathType Leaf)) {
        throw "Expected pinned GZDoom runtime dependency is missing: $runtimeSource"
    }
    Copy-Item -LiteralPath $runtimeSource -Destination $engineDir -Force
}
Write-Output $engine
