[CmdletBinding()]
param([int]$Seed = 1,
      [ValidateSet('Vulkan', 'OpenGL')][string]$Renderer = 'Vulkan',
      [string]$EngineDirectory,
      [string]$EvidenceDirectory = 'artifacts/player-projection')

. (Join-Path $PSScriptRoot 'ProjectBroom.Common.ps1')
$root = Get-ProjectBroomRoot
if (-not $EngineDirectory) { $EngineDirectory = Get-ProjectBroomEngineDirectory }
$engine = (Resolve-Path -LiteralPath $EngineDirectory).Path
$evidence = [IO.Path]::GetFullPath((Join-Path $root $EvidenceDirectory))
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$campaign = Join-Path $root "generated/seed-$Seed/ProjectBroom-seed-$Seed.pk3"
if (-not (Test-Path -LiteralPath $campaign)) { throw "Prepare seed $Seed with launch-source-bridge.ps1 first." }
$arguments = @('-stdout', '-window', '-width', '1280', '-height', '720', '-nosound',
    '-config', (Join-Path $evidence 'smoke.ini'),
    '-iwad', (Join-Path $root '.deps/freedoom-0.13.0/freedoom2.wad'),
    '-file', (Join-Path $root 'mod/BrogueDoom'), $campaign,
    '+set', 'vid_preferbackend', $(if ($Renderer -eq 'Vulkan') { '1' } else { '0' }),
    '+set', 'vid_activeinbackground', 'true', '+set', 'i_pauseinbackground', 'false',
    '+set', 'brg_seed', "$Seed", '+set', 'brg_debug', 'true',
    '+set', 'brg_projection_smoke', 'true', '+set', 'screenshot_dir', $evidence,
    '+screenblocks', '12', '+map', 'BRG01', '+brg_actions', 'N', 'N', 'N', 'N')
$logPath = Join-Path $evidence 'runtime.log'
$quoted = $arguments | ForEach-Object { '"' + $_ + '"' }
$process = Start-Process -FilePath (Join-Path $engine 'uzdoom.exe') -WorkingDirectory $engine `
    -ArgumentList $quoted -WindowStyle Hidden -PassThru -RedirectStandardOutput $logPath `
    -RedirectStandardError (Join-Path $evidence 'stderr.log')
try {
    $deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 250
        $log = Get-Content -LiteralPath $logPath -Raw
        if ($log -match 'PROJECTION_SMOKE (PASS|FAIL)') {
            $result = $Matches[1]
            Start-Sleep -Milliseconds 500
            if ($result -eq 'FAIL') { throw "Rendered player differs from Brogue: $logPath" }
            Write-Output "Player projection passed after 35 rendered frames: $logPath"
            return
        }
        if ($process.HasExited) { throw "Engine exited before projection verification: $logPath" }
    } while ((Get-Date) -lt $deadline)
    throw "Player projection check timed out: $logPath"
} finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id }
}
