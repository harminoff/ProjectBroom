[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 9223372036854775807)]
    [long] $Seed,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 40)]
    [int] $Depth,

    [string] $Output = "generated",

    [switch] $NoLaunch
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." -ChildPath ".")).Path
$python = Get-Command python.exe -ErrorAction SilentlyContinue
if ($null -eq $python) {
    throw "python.exe is required on PATH."
}

$arguments = @(
    (Join-Path $projectRoot "tools\brogue_gzmap.py"),
    "--seed", $Seed.ToString(),
    "--depth", $Depth.ToString(),
    "--output", $Output
)
if ($NoLaunch) {
    $arguments += "--no-launch"
}

& $python.Source @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Brogue map test failed with exit code $LASTEXITCODE."
}
