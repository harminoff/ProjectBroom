[CmdletBinding()]
param([string]$ResourcePackage, [string]$EvidenceDirectory, [string]$EngineDirectory, [string]$IwadPath,
      [string]$CampaignPackage,
      [ValidateSet('Vulkan', 'OpenGL')][string]$Renderer = 'Vulkan',
      [ValidateRange(1, 3)][int]$HudScale = 1)

# Runtime check for the general interaction contract (ABI v24). The engine drives
# Call, Relabel, Run, Swap, Rethrow, New Game and Abandon through the real key
# routing against a running Brogue session and prints INTERACTION_UI lines.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'ProjectBroom.Common.ps1')
if ($EngineDirectory) { $engineDir = (Resolve-Path -LiteralPath $EngineDirectory).Path }
else { $engineDir = Get-ProjectBroomEngineDirectory; Copy-ProjectBroomEngineRuntime }
if (-not $IwadPath) { $IwadPath = Join-Path $projectRoot '.deps/freedoom-0.13.0/freedoom2.wad' }
$seed = 1
$evidence = Join-Path $projectRoot "artifacts/interaction-ui-$Renderer-$HudScale"
$resources = Join-Path $projectRoot 'mod/BrogueDoom'
if ($ResourcePackage) { $resources = (Resolve-Path -LiteralPath $ResourcePackage -ErrorAction Stop).Path }
if ($EvidenceDirectory) { $evidence = [IO.Path]::GetFullPath($EvidenceDirectory) }
$campaign = $CampaignPackage
if (-not $campaign) {
    foreach ($candidate in @("generated/seed-$seed/ProjectBroom-seed-$seed.pk3", "generated/seed-$seed/startup/ProjectBroom-seed-$seed.pk3")) {
        $path = Join-Path $projectRoot $candidate
        if (Test-Path -LiteralPath $path) { $campaign = $path; break }
    }
}
if (-not $campaign -or -not (Test-Path -LiteralPath $campaign)) {
    throw "Prepare seed $seed with scripts/launch-source-bridge.ps1 -Seed $seed before running this check."
}
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$runtimeLog = Join-Path $evidence 'runtime.log'
$arguments = @(
    '-stdout', '-config', (Join-Path $evidence 'smoke.ini'), '-window', '-width', '1280', '-height', '720', '-nosound',
    '-iwad', $IwadPath,
    '-file', $resources, $campaign,
    '+set', 'brg_seed', "$seed", '+set', 'brg_debug', 'false',
    '+set', 'vid_preferbackend', $(if ($Renderer -eq 'Vulkan') { '1' } else { '0' }),
    '+set', 'brg_hud_scale', "$HudScale",
    '+screenblocks', '12', '+ucm_drawmap', 'false', '+ucm_hide', 'true',
    '+set', 'vid_activeinbackground', 'true', '+set', 'i_pauseinbackground', 'false',
    '+set', 'screenshot_dir', $evidence, '+set', 'brg_rat_walk_tics', '5',
    '+set', 'brg_monster_anim_tics', '5',
    '+set', 'brg_save_root', (Join-Path $evidence 'native-saves'),
    '+map', 'BRG01', '+brg_interaction_smoke'
)
$quotedArguments = $arguments | ForEach-Object { '"' + $_ + '"' }
$process = Start-Process -FilePath (Join-Path $engineDir 'uzdoom.exe') -WorkingDirectory $engineDir `
    -ArgumentList $quotedArguments -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $runtimeLog -RedirectStandardError (Join-Path $evidence 'stderr.log')
try {
    $deadline = (Get-Date).AddSeconds(90)
    do {
        Start-Sleep -Milliseconds 250
        $log = if (Test-Path -LiteralPath $runtimeLog) { Get-Content -LiteralPath $runtimeLog -Raw } else { '' }
        if ($log -match 'INTERACTION_UI FAIL') { throw "interaction UI regression failed; see $runtimeLog" }
        if ($log -match 'INTERACTION_UI PASS') {
            Start-Sleep -Milliseconds 500
            Write-Output "interaction UI passed. Evidence: $evidence"
            return
        }
        if ($process.HasExited) { throw "UZDoom exited before verification; see $runtimeLog" }
    } while ((Get-Date) -lt $deadline)
    throw "interaction UI check timed out; see $runtimeLog"
} finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id }
}
