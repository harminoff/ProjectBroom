[CmdletBinding()]
param([ValidateSet('gallery','before','normal')][string]$Phase='gallery')
$ErrorActionPreference='Stop'
$ratRoot=Split-Path -Parent $PSScriptRoot
$ratEvidence=Join-Path $ratRoot 'artifacts\rat-animation'
$ratArgs=@('-width','1280','-height','960','-window','-nosound',
 '-config',"$ratEvidence\$Phase.ini",'-iwad',"$ratRoot\.deps\freedoom-0.13.0\freedoom2.wad",'-file',
 $(if($Phase -eq 'before') {"$ratRoot\artifacts\creature-models\ProjectBroom-creatures.pk3"} else {"$ratEvidence\ProjectBroom-rat-animated.pk3"}))
if($Phase -eq 'normal') {
 $ratMap=Join-Path $ratRoot 'artifacts\rat-model\floor1.pk3'
 if(-not (Test-Path -LiteralPath $ratMap)) { throw 'Prepare a seed-one floor-one map PK3 for the normal encounter review.' }
 $ratArgs+=$ratMap
}
$ratArgs+="$ratEvidence\$Phase"
$ratMapName=if($Phase -eq 'normal') {'BRG01'} else {'ART01'}
$ratArgs+=@('-exec',"$ratEvidence\$Phase.cfg",'+logfile',"$ratEvidence\$Phase.log",'+map',$ratMapName)
$ratProcess=Start-Process "$ratRoot\.build\gzdoom\Release\gzdoom.exe" -ArgumentList $ratArgs -WorkingDirectory $ratRoot -WindowStyle Hidden -PassThru
Write-Output "Rat review PID $($ratProcess.Id)"
if($ratProcess.WaitForExit(45000)) { Write-Output "Exit $($ratProcess.ExitCode)" } else { Write-Output 'Review continues; the capture script exits automatically.' }
