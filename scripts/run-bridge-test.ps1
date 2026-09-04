[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [UInt64] $Seed,
    [string] $Actions = "WAIT,N,E,SE,WAIT,W",
    [UInt64] $LongRun = 0,
    [switch] $VerboseOutput
)

$projectRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot "build-bridge.ps1")

$bridgeExe = Join-Path $projectRoot "src\brogue-mapgen\bin\brogue-bridge.exe"
$arguments = @("--seed", [string] $Seed)
if ($LongRun -gt 0) {
    $arguments += @("--long-run", [string] $LongRun)
} else {
    $arguments += @("--actions", $Actions)
}
if ($VerboseOutput) {
    $arguments += "--verbose"
}

& $bridgeExe @arguments
exit $LASTEXITCODE
