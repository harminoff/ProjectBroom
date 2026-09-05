[CmdletBinding()]
param([switch]$SkipTests)

& (Join-Path $PSScriptRoot "build-dev.ps1") -SkipTests:$SkipTests
