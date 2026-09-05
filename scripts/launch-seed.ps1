# Legacy game entry point: always use the authoritative source bridge.
[CmdletBinding()]
param([ValidateRange(1, [int]::MaxValue)][int]$Seed = 1,
      [switch]$Force, [switch]$NoSound, [switch]$Wait)
$process = & (Join-Path $PSScriptRoot "launch-source-bridge.ps1") -Seed $Seed -Force:$Force -PassThru |
    Where-Object { $_ -is [System.Diagnostics.Process] } | Select-Object -Last 1
if ($Wait -and $process) { $process.WaitForExit(); exit $process.ExitCode }
