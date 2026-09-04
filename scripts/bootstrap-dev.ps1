[CmdletBinding()]
param([switch]$SkipConfigure)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$lock = Get-ProjectBroomLock
$deps = Join-Path $root ".deps"
$build = Join-Path $root ".build"
$gzdoom = Join-Path $deps "gzdoom-source"
$gzdoomRuntime = Join-Path $deps "gzdoom-runtime-4.14.2"
$freedoom = Join-Path $deps "freedoom-0.13.0"
$downloads = Join-Path $deps "downloads"
$patch = Join-Path $root $lock.components.gzdoom.patch

$git = Resolve-ProjectBroomCommand "git.exe" "Install Git for Windows."
$cmake = Resolve-ProjectBroomCommand "cmake.exe" "Install CMake and add it to PATH."
$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11 and add it to PATH."
$dotnet = Resolve-ProjectBroomCommand "dotnet.exe" "Install the .NET 8 SDK."
$null = Resolve-ProjectBroomMsysTool "make.exe"
$null = Resolve-ProjectBroomMsysTool "x86_64-w64-mingw32-gcc.exe"

$pythonVersion = (& $python --version 2>&1 | Out-String).Trim()
if ($pythonVersion -notmatch '^Python 3\.11\.') {
    throw "Python 3.11 is required; found '$pythonVersion'."
}
$dotnetMajor = [int]((& $dotnet --version 2>&1 | Out-String).Trim().Split('.')[0])
if ($dotnetMajor -lt 8) { throw ".NET SDK 8 or newer is required." }

Invoke-ProjectBroomCommand $python -Arguments @(
    "-m", "pip", "install", "--disable-pip-version-check",
    "-r", (Join-Path $root "tools\requirements-test.txt")
)

New-Item -ItemType Directory -Force -Path $deps, $build, $downloads | Out-Null

if (-not (Test-Path -LiteralPath (Join-Path $gzdoom ".git") -PathType Container)) {
    if (Test-Path -LiteralPath $gzdoom) {
        throw "Dependency path exists but is not a Git checkout: $gzdoom"
    }
    Invoke-ProjectBroomCommand $git -Arguments @("clone", "--no-checkout", $lock.components.gzdoom.source, $gzdoom)
    Invoke-ProjectBroomCommand $git -Arguments @("-C", $gzdoom, "checkout", "--detach", $lock.components.gzdoom.commit)
}

$actualCommit = (& $git -C $gzdoom rev-parse HEAD).Trim()
if ($actualCommit -ne $lock.components.gzdoom.commit) {
    throw "GZDoom checkout is $actualCommit; expected $($lock.components.gzdoom.commit). Remove .deps\gzdoom-source after preserving any work, then bootstrap again."
}

$patchMarker = Select-String -LiteralPath (Join-Path $gzdoom "src\g_game.cpp") -SimpleMatch "BrogueBridge_HandleInput" -Quiet
if (-not $patchMarker) {
    $dirty = (& $git -C $gzdoom status --porcelain | Out-String).Trim()
    if ($dirty) { throw "GZDoom dependency has unexpected local changes. Preserve them before applying the Project Broom patch." }
    Invoke-ProjectBroomCommand $git -Arguments @("-C", $gzdoom, "apply", "--check", $patch)
    Invoke-ProjectBroomCommand $git -Arguments @("-C", $gzdoom, "apply", $patch)
}

$gzdoomRuntimeArchive = Join-Path $downloads "gzdoom-4-14-2-Windows.zip"
if (-not (Test-Path -LiteralPath $gzdoomRuntimeArchive -PathType Leaf) -or
    (Get-ProjectBroomSha256 $gzdoomRuntimeArchive) -ne $lock.components.gzdoom.windowsRuntime.archiveSha256) {
    Invoke-WebRequest -Uri $lock.components.gzdoom.windowsRuntime.source -OutFile $gzdoomRuntimeArchive
}
if ((Get-ProjectBroomSha256 $gzdoomRuntimeArchive) -ne $lock.components.gzdoom.windowsRuntime.archiveSha256) {
    throw "GZDoom Windows runtime archive hash mismatch."
}
if (-not (Test-Path -LiteralPath (Join-Path $gzdoomRuntime "zmusic.dll") -PathType Leaf)) {
    Expand-Archive -LiteralPath $gzdoomRuntimeArchive -DestinationPath $gzdoomRuntime -Force
}
foreach ($runtimeFile in @(
    @{ Name = "openal32.dll"; Hash = $lock.components.gzdoom.windowsRuntime.openal32Sha256 },
    @{ Name = "sndfile.dll"; Hash = $lock.components.gzdoom.windowsRuntime.sndfileSha256 },
    @{ Name = "zmusic.dll"; Hash = $lock.components.gzdoom.windowsRuntime.zmusicSha256 }
)) {
    $runtimePath = Join-Path $gzdoomRuntime $runtimeFile.Name
    if (-not (Test-Path -LiteralPath $runtimePath -PathType Leaf) -or
        (Get-ProjectBroomSha256 $runtimePath) -ne $runtimeFile.Hash) {
        throw "GZDoom runtime dependency hash mismatch: $($runtimeFile.Name)"
    }
}

$correspondingSources = @(
    @{ Name = "zmusic-source"; Component = $lock.components.zmusic },
    @{ Name = "libsndfile-source"; Component = $lock.components.libsndfile },
    @{ Name = "openal-soft-source"; Component = $lock.components.openalSoft }
)
foreach ($sourceDependency in $correspondingSources) {
    $checkout = Join-Path $deps $sourceDependency.Name
    if (-not (Test-Path -LiteralPath (Join-Path $checkout ".git") -PathType Container)) {
        if (Test-Path -LiteralPath $checkout) { throw "Dependency path exists but is not a Git checkout: $checkout" }
        Invoke-ProjectBroomCommand $git -Arguments @("clone", "--no-checkout", $sourceDependency.Component.source, $checkout)
        Invoke-ProjectBroomCommand $git -Arguments @("-C", $checkout, "checkout", "--detach", $sourceDependency.Component.commit)
    }
    $sourceCommit = (& $git -C $checkout rev-parse HEAD).Trim()
    if ($sourceCommit -ne $sourceDependency.Component.commit) {
        throw "$($sourceDependency.Name) is $sourceCommit; expected $($sourceDependency.Component.commit)."
    }
}

$freedoomArchive = Join-Path $downloads "freedoom-0.13.0.zip"
if (-not (Test-Path -LiteralPath $freedoomArchive -PathType Leaf) -or
    (Get-ProjectBroomSha256 $freedoomArchive) -ne $lock.components.freedoom.archiveSha256) {
    Invoke-WebRequest -Uri $lock.components.freedoom.source -OutFile $freedoomArchive
}
if ((Get-ProjectBroomSha256 $freedoomArchive) -ne $lock.components.freedoom.archiveSha256) {
    throw "Freedoom archive hash mismatch."
}
if (-not (Test-Path -LiteralPath (Join-Path $freedoom "freedoom2.wad") -PathType Leaf)) {
    Expand-Archive -LiteralPath $freedoomArchive -DestinationPath $deps -Force
}
$freedoomWad = Join-Path $freedoom "freedoom2.wad"
if ((Get-ProjectBroomSha256 $freedoomWad) -ne $lock.components.freedoom.freedoom2Sha256) {
    throw "Freedoom Phase 2 hash mismatch."
}

if (-not $SkipConfigure) {
    $engineBuild = Join-Path $build "gzdoom"
    Invoke-ProjectBroomCommand $cmake -Arguments @("-S", $gzdoom, "-B", $engineBuild, "-G", "Visual Studio 17 2022", "-A", "x64")
}

Write-Output "Project Broom dependencies are ready."
Write-Output "GZDoom: $gzdoom ($actualCommit)"
Write-Output "GZDoom runtime dependencies: $gzdoomRuntime"
Write-Output "Freedoom: $freedoomWad"
