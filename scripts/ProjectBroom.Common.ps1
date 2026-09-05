Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ProjectBroomRoot {
    return (Split-Path -Parent $PSScriptRoot)
}

function Get-ProjectBroomLock {
    $path = Join-Path (Get-ProjectBroomRoot) "dependencies.lock.json"
    return (Get-Content -Raw -LiteralPath $path | ConvertFrom-Json)
}

function Get-ProjectBroomSha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-ProjectBroomRelativePath([string]$BasePath, [string]$Path) {
    $baseFull = [IO.Path]::GetFullPath($BasePath).TrimEnd('\') + '\'
    $pathFull = [IO.Path]::GetFullPath($Path)
    $baseUri = New-Object Uri($baseFull)
    $pathUri = New-Object Uri($pathFull)
    return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace('/', '\')
}

function Invoke-ProjectBroomCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @()
    )
    if ([IO.Path]::GetFileNameWithoutExtension($FilePath) -eq "cmake") {
        $python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."
        & $python (Join-Path (Get-ProjectBroomRoot) "tools\run_native.py") $FilePath @Arguments
    } else {
        & $FilePath @Arguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

function Get-ProjectBroomEngineDirectory {
    $build = Join-Path (Get-ProjectBroomRoot) ".build\uzdoom"
    foreach ($directory in @((Join-Path $build "Release"), $build)) {
        if (Test-Path -LiteralPath (Join-Path $directory "uzdoom.exe") -PathType Leaf) { return $directory }
    }
    throw "Custom UZDoom is missing. Run scripts/build-dev.ps1."
}

function Copy-ProjectBroomEngineRuntime {
    $root = Get-ProjectBroomRoot
    $lock = Get-ProjectBroomLock
    $target = Get-ProjectBroomEngineDirectory
    $runtime = Join-Path $root ".deps\uzdoom-runtime-5.0.0"
    foreach ($file in $lock.components.uzdoom.windowsRuntime.files) {
        $source = Join-Path $runtime $file.path
        if ((Get-ProjectBroomSha256 $source) -ne $file.sha256) { throw "UZDoom dependency hash mismatch: $($file.path)" }
        $destination = Join-Path $target $file.path
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        if (-not (Test-Path -LiteralPath $destination) -or (Get-ProjectBroomSha256 $destination) -ne $file.sha256) {
            Copy-Item -LiteralPath $source -Destination $destination -Force
        }
    }
    $bridge = Join-Path $root "src\brogue-mapgen\bin\brogue-bridge.dll"
    $destination = Join-Path $target "brogue-bridge.dll"
    if (-not (Test-Path -LiteralPath $destination) -or (Get-ProjectBroomSha256 $destination) -ne (Get-ProjectBroomSha256 $bridge)) {
        Copy-Item -LiteralPath $bridge -Destination $destination -Force
    }
}

function Resolve-ProjectBroomCommand([string]$Name, [string]$Help) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) { throw "$Name was not found. $Help" }
    return $command.Source
}

function Resolve-ProjectBroomMsysTool([string]$Name) {
    $roots = @()
    if ($env:PROJECTBROOM_MSYS2_ROOT) { $roots += $env:PROJECTBROOM_MSYS2_ROOT }
    $roots += @("C:\msys64", "C:\tools\msys64")
    foreach ($root in $roots) {
        foreach ($bin in @("ucrt64\bin", "mingw64\bin", "usr\bin")) {
            $candidate = Join-Path (Join-Path $root $bin) $Name
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
        }
    }
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    throw "$Name was not found. Install MSYS2 UCRT64 make/GCC or set PROJECTBROOM_MSYS2_ROOT."
}

function Enable-ProjectBroomMsysPath([string[]]$ToolPaths) {
    $directories = @($ToolPaths | ForEach-Object { Split-Path -Parent $_ })
    foreach ($toolPath in $ToolPaths) {
        $directory = Split-Path -Parent $toolPath
        $parent = Split-Path -Parent $directory
        if ((Split-Path -Leaf $parent) -in @("ucrt64", "mingw64", "usr")) {
            $msysRoot = Split-Path -Parent $parent
            $usrBin = Join-Path $msysRoot "usr\bin"
            if (Test-Path -LiteralPath $usrBin -PathType Container) { $directories += $usrBin }
        }
    }
    $directories = @($directories | Select-Object -Unique)
    $env:Path = (($directories + @($env:Path)) -join ";")
}
