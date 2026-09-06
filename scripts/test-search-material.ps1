[CmdletBinding()]
param([ValidateSet('Vulkan','OpenGL')][string]$Renderer='Vulkan',
      [ValidateRange(1,3)][int]$HudScale=1)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'ProjectBroom.Common.ps1')
$root=Get-ProjectBroomRoot
$engine=Get-ProjectBroomEngineDirectory
Copy-ProjectBroomEngineRuntime
$evidence=Join-Path $root "artifacts/search-material-final-$Renderer-$HudScale"
New-Item -ItemType Directory -Force $evidence | Out-Null
$runtimeLog=Join-Path $evidence 'runtime.log'
$arguments=@('-stdout','-config',(Join-Path $evidence 'smoke.ini'),'-window','-width','1280','-height','720','-nosound',
 '-iwad',(Join-Path $root '.deps/freedoom-0.13.0/freedoom2.wad'),
 '-file',(Join-Path $root 'mod/BrogueDoom'),(Join-Path $root 'generated/seed-1/ProjectBroom-seed-1.pk3'),
 '+set','brg_seed','1','+set','vid_preferbackend',$(if($Renderer -eq 'Vulkan'){'1'}else{'0'}),
 '+set','brg_hud_scale',"$HudScale",'+set','vid_activeinbackground','true','+set','i_pauseinbackground','false',
 '+screenblocks','12','+set','screenshot_dir',$evidence,'+map','BRG01','+brg_reveal_material_smoke')
$quotedArguments=$arguments | ForEach-Object {'"'+$_+'"'}
$process=Start-Process -FilePath (Join-Path $engine 'uzdoom.exe') -WorkingDirectory $engine -ArgumentList $quotedArguments -WindowStyle Hidden -PassThru -RedirectStandardOutput $runtimeLog -RedirectStandardError (Join-Path $evidence 'stderr.log')
try {
 $deadline=(Get-Date).AddSeconds(50)
 do {
  Start-Sleep -Milliseconds 250
  $log=if(Test-Path $runtimeLog){Get-Content $runtimeLog -Raw}else{''}
  if($log -match 'REVEAL_MATERIAL FAIL'){throw "Material smoke failed: $runtimeLog"}
  if($log -match 'REVEAL_MATERIAL PASS'){Write-Output "Material smoke complete: $evidence"; return}
  if($process.HasExited){throw "UZDoom exited: $runtimeLog"}
 } while((Get-Date) -lt $deadline)
 throw "Material smoke timed out: $runtimeLog"
} finally {if(-not $process.HasExited){Stop-Process -Id $process.Id}}
