[CmdletBinding()]
param([switch]$Wand, [switch]$Throw, [string]$ResourcePackage, [string]$EvidenceDirectory,
      [string]$EngineDirectory, [string]$IwadPath,
      [ValidateSet('Vulkan', 'OpenGL')][string]$Renderer = 'Vulkan',
      [ValidateRange(1, 3)][int]$HudScale = 1)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'ProjectBroom.Common.ps1')
if ($EngineDirectory) { $engineDir = (Resolve-Path -LiteralPath $EngineDirectory).Path }
else { $engineDir = Get-ProjectBroomEngineDirectory; Copy-ProjectBroomEngineRuntime }
if (-not $IwadPath) { $IwadPath = Join-Path $projectRoot '.deps/freedoom-0.13.0/freedoom2.wad' }
$device = if ($Throw) { 'throw' } elseif ($Wand) { 'wand' } else { 'staff' }
$seed = if ($Throw) { 1 } elseif ($Wand) { 19 } else { 14 }
$label = $device.ToUpperInvariant() + '_UI'
$actions = if ($Throw) { '' } elseif ($Wand) {
    'N N N N NE N NE NE E E E E E E E E N N N E E E E E E E E E E E N N N N E E E E E E E SE SE SE SE SE SE'
} else {
    'N N N N N NE NE NE E E N N N N N N N E E NE NE NE NE E E E E E E E E E E E E E E E E E NE E'
}
$evidence = Join-Path $projectRoot "artifacts/$device-ui-$Renderer-$HudScale"
$resources = Join-Path $projectRoot 'mod/BrogueDoom'
if ($ResourcePackage) {
    $resources = (Resolve-Path -LiteralPath $ResourcePackage -ErrorAction Stop).Path
    $evidence = Join-Path $projectRoot "artifacts/$device-ui-packaged-$Renderer-$HudScale"
}
if ($EvidenceDirectory) { $evidence = [IO.Path]::GetFullPath($EvidenceDirectory) }
$campaign = Join-Path $projectRoot "generated/seed-$seed/ProjectBroom-seed-$seed.pk3"
if (-not (Test-Path -LiteralPath $campaign)) {
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
    '+map', 'BRG01', "+brg_${device}_smoke", '+brg_actions'
) + @($actions.Split(' ') | Where-Object { $_ })
# Quote paths for Start-Process's Windows argument-string boundary.
$quotedArguments = $arguments | ForEach-Object { '"' + $_ + '"' }
$process = Start-Process -FilePath (Join-Path $engineDir 'uzdoom.exe') -WorkingDirectory $engineDir `
    -ArgumentList $quotedArguments -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $runtimeLog -RedirectStandardError (Join-Path $evidence 'stderr.log')
try {
    $deadline = (Get-Date).AddSeconds(60)
    do {
        Start-Sleep -Milliseconds 250
        $log = if (Test-Path -LiteralPath $runtimeLog) { Get-Content -LiteralPath $runtimeLog -Raw } else { '' }
        if ($log -match "$label FAIL") { throw "$device UI regression failed; see $runtimeLog" }
        if ($log -match "$label capture phase=10" -and $log -match "$label PASS" -and $log -match "$label cancel unchanged=true") {
            # Let the engine complete its deferred framebuffer capture.
            Start-Sleep -Milliseconds 500
            Write-Output "$device UI passed: cancellation preserved state and firing advanced one revision. Evidence: $evidence"
            return
        }
        if ($process.HasExited) { throw "UZDoom exited before $device verification; see $runtimeLog" }
    } while ((Get-Date) -lt $deadline)
    throw "$device UI check timed out; see $runtimeLog"
} finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id }
}
