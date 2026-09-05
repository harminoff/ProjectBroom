[CmdletBinding()]
param()

& (Join-Path $PSScriptRoot 'test-staff-ui.ps1') -Wand
