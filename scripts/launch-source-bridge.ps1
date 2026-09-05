[CmdletBinding()]
param(
    [ValidateRange(1, [int]::MaxValue)]
    [int]$Seed = 1,
    [switch]$RandomSeed,
    [switch]$Force,
    [switch]$Menu,
    [switch]$ShowFPS,
    [ValidateRange(320, 7680)]
    [int]$WindowWidth = 1280,
    [ValidateRange(240, 4320)]
    [int]$WindowHeight = 720,
    [ValidateRange(0, [int]::MaxValue)]
    [int]$ComparePid = 0,
    [ValidateRange(1.0, 3.0)]
    [double]$HudScale = 1.0,
    [switch]$PassThru
)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$projectRoot = Get-ProjectBroomRoot
$ErrorActionPreference = "Stop"

function Get-BrogueSha256([string]$Path) {
    $stream = [System.IO.File]::OpenRead($Path)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    } finally {
        $hasher.Dispose()
        $stream.Dispose()
    }
}

function Copy-BrogueFileIfDifferent([string]$Source, [string]$Destination) {
    if ((Test-Path -LiteralPath $Destination -PathType Leaf) -and
        (Get-BrogueSha256 $Source) -eq (Get-BrogueSha256 $Destination)) {
        return
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

if ($RandomSeed) {
    $seedBytes = New-Object byte[] 4
    $seedGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $seedGenerator.GetBytes($seedBytes) } finally { $seedGenerator.Dispose() }
    $Seed = [int](([BitConverter]::ToUInt32($seedBytes, 0) % 2147483646) + 1)
}
$engineDir = Get-ProjectBroomEngineDirectory
$engine = Join-Path $engineDir "uzdoom.exe"
Copy-ProjectBroomEngineRuntime
$bridge = Join-Path $projectRoot "src\brogue-mapgen\bin\brogue-bridge.dll"
$exporter = Join-Path $projectRoot "src\brogue-mapgen\bin\brogue.exe"
$iwad = Join-Path $projectRoot ".deps\freedoom-0.13.0\freedoom2.wad"
$configuration = Join-Path $env:LOCALAPPDATA "ProjectBroom\config"
New-Item -ItemType Directory -Force -Path $configuration | Out-Null
$engineConfig = Join-Path $configuration "uzdoom.ini"
$oldConfig = Join-Path $configuration "gzdoom.ini"
if (-not (Test-Path -LiteralPath $engineConfig) -and (Test-Path -LiteralPath $oldConfig)) {
    Copy-Item -LiteralPath $oldConfig -Destination $engineConfig
}
$staticMod = Join-Path $projectRoot "mod\BrogueDoom"
$textureRegistry = Join-Path $projectRoot "assets\terrain\broguedoom_cave_registry.json"
$monsterRegistry = Join-Path $projectRoot "assets\monsters\brogue_monster_registry.json"
$monsterAtlas = Join-Path $projectRoot "mod\BrogueDoom\graphics\BRGMON.png"
$weaponRegistry = Join-Path $projectRoot "assets\weapons\brogue_weapon_registry.json"
$weaponModeldef = Join-Path $projectRoot "mod\BrogueDoom\models\weapons\MODELDEF.txt"
$compiler = Join-Path $projectRoot "tools\mapcompiler\compile.py"
$verifier = Join-Path $projectRoot "tools\mapcompiler\verify.py"
$generated = Join-Path $projectRoot ("generated\seed-{0}\ProjectBroom-seed-{0}.pk3" -f $Seed)
$json = Join-Path $projectRoot ("generated\seed-{0}\brogue-dungeon.json" -f $Seed)
$packageManifest = Join-Path $projectRoot ("generated\seed-{0}\brogue-manifest.json" -f $Seed)
$engineBridge = Join-Path $engineDir "brogue-bridge.dll"

foreach ($required in @($engine, $bridge, $exporter, $iwad, $textureRegistry, $monsterRegistry, $monsterAtlas, $weaponRegistry, $weaponModeldef, $compiler, $verifier)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required source-bridge artifact is missing: $required"
    }
}
$pythonCommand = Get-Command python.exe -ErrorAction Stop
$generatedRoot = Split-Path -Parent $generated
New-Item -ItemType Directory -Force -Path $generatedRoot | Out-Null
if ($Force -or -not (Test-Path -LiteralPath $json -PathType Leaf)) {
    Write-Output "Generating Brogue dungeon for random seed $Seed..."
    & $exporter --export-dungeon-json $json --seed $Seed --depths 40
    if ($LASTEXITCODE -ne 0) { throw "Brogue export failed with exit code $LASTEXITCODE." }
} else {
    Write-Output "Using cached Brogue dungeon for seed $Seed."
}
$inputHash = Get-BrogueSha256 $json
$needsPackage = $Force -or -not (Test-Path -LiteralPath $generated -PathType Leaf) -or -not (Test-Path -LiteralPath $packageManifest -PathType Leaf)
if (-not $needsPackage) {
    try {
        $manifest = Get-Content -Raw -LiteralPath $packageManifest | ConvertFrom-Json
        $needsPackage = $manifest.inputSha256 -ne $inputHash -or $manifest.compilerVersion -ne "42" -or $manifest.resourcePack -ne "Project Broom Original Cave Textures"
    } catch {
        $needsPackage = $true
    }
}
if ($needsPackage) {
    Write-Output "Compiling the Brogue dungeon into UZDoom maps..."
    & $pythonCommand.Source $compiler --input $json --output $generated
    if ($LASTEXITCODE -ne 0) { throw "PK3 compilation failed with exit code $LASTEXITCODE." }
} else {
    Write-Output "Using cached UZDoom campaign for seed $Seed."
}

Write-Output "Verifying map topology and package integrity..."
& $pythonCommand.Source $verifier --input $json --package $generated
if ($LASTEXITCODE -ne 0) { throw "Generated package verification failed with exit code $LASTEXITCODE." }

Copy-BrogueFileIfDifferent $bridge $engineBridge

$arguments = @(
    "-width", $WindowWidth,
    "-height", $WindowHeight,
    "-nosound",
    "-config", $engineConfig,
    "-iwad", $iwad,
    "-file", $staticMod, $generated,
    "+set", "brg_seed", $Seed,
    "+set", "brg_hud_scale", $HudScale.ToString([System.Globalization.CultureInfo]::InvariantCulture),
    "+set", "brg_debug", "false",
    "+ucm_hide", "true",
    "+ucm_drawmap", "false",
    "+ucm_mapshowall", "false",
    "+screenblocks", "12",
    "+set", "brg_monster_anim_tics", "5",
    "+set", "brg_monster_omniscience", "false"
)
if ($Menu) {
    $arguments += @("+menu_main")
} else {
    $arguments += @("+map", "BRG01")
}
if ($ComparePid -gt 0) {
    $arguments += @("+set", "brg_compare_pid", $ComparePid)
}
if ($ShowFPS) {
    $arguments += @("+vid_fps", "true")
}

Write-Output "Launching UZDoom for seed $Seed..."
$process = Start-Process -FilePath $engine -WorkingDirectory $engineDir -ArgumentList $arguments -PassThru
Write-Output "Project Broom prepared seed $Seed."
if ($PassThru) {
    Write-Output $process
} else {
    Write-Output "Started source-built UZDoom PID $($process.Id) with Brogue bridge seed $Seed."
}
