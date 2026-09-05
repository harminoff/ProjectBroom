[CmdletBinding()]
param([switch]$Quick)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."

Push-Location $root
try {
    & (Join-Path $PSScriptRoot "audit-public-tree.ps1") -WorkingTree
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_brogue_bridge", "tools.test_broguedoom_resources", "tools.monster_models.test_rat", "tools.monster_models.test_rat_animation", "tools.monster_models.test_creatures", "tools.weapon_models.test_viewmodel", "tools.pickup_models.test_detailed", "tools.mapcompiler.test_compile")
    if (-not $Quick) {
        & (Join-Path $PSScriptRoot "run-bridge-test.ps1") -Seed 1 -LongRun 300
    }
} finally { Pop-Location }

Write-Output "Project Broom tests passed."
