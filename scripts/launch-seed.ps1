param(
    [Parameter(Mandatory = $false)]
    [ValidateRange(1, [UInt64]::MaxValue)]
    [UInt64] $Seed = 1,
    [switch] $Force,
    [switch] $NoSound,
    [switch] $Wait
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = Join-Path $projectRoot "src\brogue-mapgen"
$exporter = Join-Path $sourceRoot "bin\brogue.exe"
$upstreamMetadata = Join-Path $sourceRoot "UPSTREAM.md"
$compiler = Join-Path $projectRoot "tools\mapcompiler\compile.py"
$gzdoom = Join-Path $projectRoot "tooling\GZDoom\gzdoom.exe"
$iwad = Join-Path $projectRoot "tooling\GZDoom\freedoom2.wad"
$staticMod = Join-Path $projectRoot "mod\BrogueDoom"
$minimapScript = Join-Path $staticMod "ucm\ucm_minimap.zsc"
$minimapCvarInfo = Join-Path $staticMod "CVARINFO.txt"
$minimapKeyConf = Join-Path $staticMod "KEYCONF.txt"
$textureRegistry = Join-Path $projectRoot "assets\terrain\broguedoom_cave_registry.json"
$seedRoot = Join-Path $projectRoot ("generated\seed-{0}" -f $Seed)
$jsonPath = Join-Path $seedRoot "brogue-dungeon.json"
$pk3Path = Join-Path $seedRoot ("ProjectBroom-seed-{0}.pk3" -f $Seed)
$manifestPath = Join-Path $seedRoot "brogue-manifest.json"

foreach ($requiredPath in @($exporter, $upstreamMetadata, $compiler, $gzdoom, $iwad, $staticMod, $minimapScript, $minimapCvarInfo, $minimapKeyConf, $textureRegistry)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required path is missing: $requiredPath"
    }
}
$pinnedCommit = "7f52dd93b7fa553dd6e354ccd44229a3c22d8a76"
if (-not (Get-Content -Raw -LiteralPath $upstreamMetadata).Contains($pinnedCommit)) {
    throw "Exporter snapshot is not pinned to the required Brogue CE commit."
}
$exporterVersion = (& $exporter --version 2>&1 | Out-String).Trim()
if ($exporterVersion -notmatch "Brogue version:\s+CE ") {
    throw "The configured exporter did not identify itself as Brogue CE: '$exporterVersion'."
}

$gzdoomVersion = (Get-Item -LiteralPath $gzdoom).VersionInfo.ProductVersionRaw.ToString()
if ($gzdoomVersion -notmatch "^4\.14\.2\.") {
    throw "GZDoom 4.14.2 is required; found '$gzdoomVersion'."
}

$pythonCommand = Get-Command python.exe -ErrorAction Stop
$pythonVersion = (& $pythonCommand.Source --version 2>&1 | Out-String).Trim()
if ($pythonVersion -notmatch "^Python 3\.11\.") {
    throw "Python 3.11 is required; found '$pythonVersion'."
}

New-Item -ItemType Directory -Force -Path $seedRoot | Out-Null
$needsJson = $Force -or -not (Test-Path -LiteralPath $jsonPath)
if ($needsJson) {
    & $exporter --export-dungeon-json $jsonPath --seed $Seed --depths 40
    if ($LASTEXITCODE -ne 0) { throw "Brogue export failed with exit code $LASTEXITCODE." }
}

$inputHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $jsonPath).Hash.ToLowerInvariant()
$needsPackage = $Force -or -not (Test-Path -LiteralPath $pk3Path) -or -not (Test-Path -LiteralPath $manifestPath)
if (-not $needsPackage) {
    try {
        $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
        $needsPackage = $manifest.inputSha256 -ne $inputHash -or $manifest.compilerVersion -ne "41" -or $manifest.resourcePack -ne "Project Broom Original Cave Textures"
    }
    catch {
        $needsPackage = $true
    }
}

if ($needsPackage) {
    & $pythonCommand.Source $compiler --input $jsonPath --output $pk3Path
    if ($LASTEXITCODE -ne 0) { throw "PK3 compilation failed with exit code $LASTEXITCODE." }
}

$verifier = Join-Path $projectRoot "tools\mapcompiler\verify.py"
& $pythonCommand.Source $verifier --input $jsonPath --package $pk3Path
if ($LASTEXITCODE -ne 0) { throw "Generated package verification failed with exit code $LASTEXITCODE." }

$arguments = @("-width", "1280", "-height", "720", "-iwad", $iwad, "-file", $staticMod, $pk3Path, "+ucm_hide", "false", "+ucm_drawmap", "true", "+ucm_radardist", "256", "+ucm_mapshowall", "true", "+map", "BRG01")
if ($NoSound) {
    $arguments = @("-nosound") + $arguments
}
$process = Start-Process -FilePath $gzdoom -WorkingDirectory $projectRoot -ArgumentList ($arguments -join " ") -WindowStyle Normal -PassThru
Write-Output ("Launched GZDoom PID {0} with seed {1}." -f $process.Id, $Seed)
if ($Wait) {
    $process.WaitForExit()
    exit $process.ExitCode
}
