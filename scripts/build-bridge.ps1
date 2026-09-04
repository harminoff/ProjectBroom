[CmdletBinding()]
param()

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$projectRoot = Get-ProjectBroomRoot
$sourceRoot = Join-Path $projectRoot "src\brogue-mapgen"
$make = Resolve-ProjectBroomMsysTool "make.exe"
$gcc = Resolve-ProjectBroomMsysTool "x86_64-w64-mingw32-gcc.exe"
$sh = Resolve-ProjectBroomMsysTool "sh.exe"
Enable-ProjectBroomMsysPath @($make, $gcc, $sh)
$makeShell = $sh.Replace('\', '/')

Push-Location $sourceRoot
try {
    & $make "SHELL=$makeShell" SYSTEM=WINDOWS GRAPHICS=NO RELEASE=YES BRIDGE=YES bin/brogue-bridge.exe bin/brogue-bridge.dll
    if ($LASTEXITCODE -ne 0) {
        throw "Brogue bridge build failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}

Write-Output (Join-Path $sourceRoot "bin\brogue-bridge.exe")
Write-Output (Join-Path $sourceRoot "bin\brogue-bridge.dll")
