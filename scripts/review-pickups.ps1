[CmdletBinding()]
param([ValidateSet('before','after','normal-before','normal-after')][string]$Phase='after')
$ErrorActionPreference='Stop'
$pickupRoot=Split-Path -Parent $PSScriptRoot
$pickupOut=Join-Path $pickupRoot 'artifacts\pickup-models'
$pickupArgs=@('-stdout','-width','1280','-height','960','-window','-nosound','-config',"$pickupOut\$Phase.ini",
 '-iwad',"$pickupRoot\.deps\freedoom-0.13.0\freedoom2.wad",'-file',"$pickupOut\ProjectBroom-pickups.pk3")
if($Phase.EndsWith('before')) { $pickupArgs+="$pickupOut\before-override" }
$pickupMap='ART01'
if($Phase.StartsWith('normal')) {
 $pickupArgs+=@("$pickupRoot\artifacts\rat-model\floor1.pk3","$pickupOut\normal")
 $pickupMap='BRG01'
} else { $pickupArgs+="$pickupOut\gallery" }
$pickupArgs+=@('-exec',"$pickupOut\$Phase.cfg",'+logfile',"$pickupOut\$Phase.log",'+map',$pickupMap)
$pickupProcess=Start-Process "$pickupRoot\.build\uzdoom\Release\uzdoom.exe" -ArgumentList $pickupArgs -WorkingDirectory $pickupRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput "$pickupOut\$Phase-stdout.log" -RedirectStandardError "$pickupOut\$Phase-stderr.log"
Write-Output "Pickup gallery PID $($pickupProcess.Id)"
if($pickupProcess.WaitForExit(45000)) { Write-Output "Exit $($pickupProcess.ExitCode)" } else { Write-Output 'Gallery is continuing; its capture script quits automatically.' }
