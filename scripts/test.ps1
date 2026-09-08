[CmdletBinding()]
param([switch]$Quick)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$python = Resolve-ProjectBroomCommand "python.exe" "Install Python 3.11."

Push-Location $root
try {
    & (Join-Path $PSScriptRoot "audit-public-tree.ps1") -WorkingTree
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_brogue_bridge", "tools.test_brogue_saves", "tools.test_broguedoom_resources", "tools.monster_models.test_rat", "tools.monster_models.test_rat_animation", "tools.monster_models.test_skeletal", "tools.monster_models.test_kobold_materials", "tools.monster_models.test_jackal", "tools.monster_models.test_monkey", "tools.monster_models.test_creatures", "tools.weapon_models.test_viewmodel", "tools.weapon_models.test_devices", "tools.pickup_models.test_detailed", "tools.mapcompiler.test_compile")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_engine_source", "tools.test_enemy_movement", "tools.test_held_movement")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.monster_models.test_connected_skin")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_native_interactions")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.search_models.test_generate")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.mapcompiler.test_terrain_geometry")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_terrain_sync")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_terrain_animation", "tools.test_bloodwort")
    Invoke-ProjectBroomCommand $python -Arguments @("-m", "unittest", "tools.test_shoreline", "tools.test_gas_assets")
    if (-not $Quick) {
        & (Join-Path $PSScriptRoot "run-bridge-test.ps1") -Seed 1 -LongRun 300
    }
} finally { Pop-Location }

Write-Output "Project Broom tests passed."
