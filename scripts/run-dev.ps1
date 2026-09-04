[CmdletBinding()]
param(
    [ValidateRange(1, [int]::MaxValue)][int]$Seed = 1,
    [switch]$RandomSeed,
    [switch]$Menu,
    [switch]$ShowFPS
)

$arguments = @("-Seed", $Seed)
if ($RandomSeed) { $arguments += "-RandomSeed" }
if ($Menu) { $arguments += "-Menu" }
if ($ShowFPS) { $arguments += "-ShowFPS" }
& (Join-Path $PSScriptRoot "launch-source-bridge.ps1") @arguments
