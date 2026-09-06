[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'ProjectBroom.Common.ps1')
$root=Get-ProjectBroomRoot
$source=Join-Path $root 'src/brogue-mapgen'
$output=Join-Path $root 'artifacts/search-standalone'
New-Item -ItemType Directory -Force $output | Out-Null
$make=Resolve-ProjectBroomMsysTool 'make.exe'
$gcc=Resolve-ProjectBroomMsysTool 'x86_64-w64-mingw32-gcc.exe'
$sh=Resolve-ProjectBroomMsysTool 'sh.exe'
$compilerBin=Split-Path $gcc -Parent
$sdl=Join-Path $compilerBin 'sdl2-config'
if(-not(Test-Path $sdl)){throw "Missing SDL2 development tool: $sdl"}
$savedPath=$env:Path
$exporter=Join-Path $source 'bin/brogue.exe'
$backup=Join-Path $output 'exporter-before-build.exe'
Copy-Item -LiteralPath $exporter -Destination $backup
Enable-ProjectBroomMsysPath @($make,$gcc,$sh)
Push-Location $source
try {
 & $make ('SHELL='+$sh.Replace('\','/')) SYSTEM=WINDOWS GRAPHICS=YES RELEASE=YES ('SDL_CONFIG='+$sdl.Replace('\','/')) bin/brogue.exe
 if($LASTEXITCODE -ne 0){throw 'SDL standalone build failed.'}
 Copy-Item bin/brogue.exe (Join-Path $output 'brogue.exe')
 Copy-Item bin/assets $output -Recurse -Force
 Copy-Item bin/keymap.txt $output
 foreach($name in @('SDL2.dll','SDL2_image.dll')){Copy-Item (Join-Path $compilerBin $name) $output}
} finally {
 Copy-Item -LiteralPath $backup -Destination $exporter -Force
 $env:Path=$savedPath
 Pop-Location
}
Write-Output (Join-Path $output 'brogue.exe')
