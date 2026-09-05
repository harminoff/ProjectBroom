[CmdletBinding()]
param([switch]$SkipConfigure)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$lock = Get-ProjectBroomLock
$deps = Join-Path $root ".deps"
$build = Join-Path $root ".build"
$uzdoom = Join-Path $deps "uzdoom-source"
$uzdoomRuntime = Join-Path $deps "uzdoom-runtime-5.0.0"
$freedoom = Join-Path $deps "freedoom-0.13.0"
$downloads = Join-Path $deps "downloads"
$patch = Join-Path $root $lock.components.uzdoom.patch

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

if (-not (Test-Path -LiteralPath (Join-Path $uzdoom ".git") -PathType Container)) {
    if (Test-Path -LiteralPath $uzdoom) {
        throw "Dependency path exists but is not a Git checkout: $uzdoom"
    }
    Invoke-ProjectBroomCommand $git -Arguments @("clone", "--no-checkout", $lock.components.uzdoom.source, $uzdoom)
    Invoke-ProjectBroomCommand $git -Arguments @("-C", $uzdoom, "checkout", "--detach", $lock.components.uzdoom.commit)
}

$actualCommit = (& $git -C $uzdoom rev-parse HEAD).Trim()
if ($actualCommit -ne $lock.components.uzdoom.commit) {
    throw "UZDoom checkout is $actualCommit; expected $($lock.components.uzdoom.commit). Remove .deps\uzdoom-source after preserving any work, then bootstrap again."
}

Invoke-ProjectBroomCommand $python -Arguments @((Join-Path $root "tools\engine_source.py"), "--root", $root, "--apply")

$uzdoomRuntimeArchive = Join-Path $downloads "uzdoom-5.0.0-Windows.zip"
if (-not (Test-Path -LiteralPath $uzdoomRuntimeArchive -PathType Leaf) -or
    (Get-ProjectBroomSha256 $uzdoomRuntimeArchive) -ne $lock.components.uzdoom.windowsRuntime.archiveSha256) {
    Invoke-WebRequest -Uri $lock.components.uzdoom.windowsRuntime.source -OutFile $uzdoomRuntimeArchive
}
if ((Get-ProjectBroomSha256 $uzdoomRuntimeArchive) -ne $lock.components.uzdoom.windowsRuntime.archiveSha256) {
    throw "UZDoom Windows runtime archive hash mismatch."
}
if (-not (Test-Path -LiteralPath (Join-Path $uzdoomRuntime "soft_oal.dll") -PathType Leaf)) {
    Expand-Archive -LiteralPath $uzdoomRuntimeArchive -DestinationPath $uzdoomRuntime -Force
}
foreach ($runtimeFile in $lock.components.uzdoom.windowsRuntime.files) {
    $runtimePath = Join-Path $uzdoomRuntime $runtimeFile.path
    if (-not (Test-Path -LiteralPath $runtimePath -PathType Leaf) -or
        (Get-ProjectBroomSha256 $runtimePath) -ne $runtimeFile.sha256) {
        throw "UZDoom runtime dependency hash mismatch: $($runtimeFile.path)"
    }
}

$correspondingSources = @(
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
    $engineBuild = Join-Path $build "uzdoom"
    Invoke-ProjectBroomCommand $cmake -Arguments @("-S", $uzdoom, "-B", $engineBuild, "-G", "Visual Studio 17 2022", "-A", "x64", "-DPROJECT_BROOM_ROOT=$($root.Replace('\', '/'))", "-DUSE_UPDATER=OFF", "-DHAVE_VULKAN=ON")
}

Write-Output "Project Broom dependencies are ready."
Write-Output "UZDoom: $uzdoom ($actualCommit)"
Write-Output "UZDoom runtime dependencies: $uzdoomRuntime"
Write-Output "Freedoom: $freedoomWad"
