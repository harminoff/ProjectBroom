[CmdletBinding()]
param(
    [switch]$SelfContained,
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $projectRoot "tools\BrogueDoomLauncher\BrogueDoomLauncher.csproj"
if (-not $OutputDirectory) {
    $OutputDirectory = if ($SelfContained) { ".build\launcher" } else { "artifacts\ProjectBroomLauncher" }
}
$publishRoot = Join-Path $projectRoot $OutputDirectory
$launcher = Join-Path $publishRoot "ProjectBroom.exe"
$rootLauncher = Join-Path $projectRoot "ProjectBroom.exe"

$arguments = @("publish", $project, "-c", "Release", "-o", $publishRoot, "--nologo")
if ($SelfContained) {
    $arguments += @("-r", "win-x64", "--self-contained", "true", "-p:PublishSingleFile=true", "-p:IncludeNativeLibrariesForSelfExtract=true")
}
& dotnet @arguments
if ($LASTEXITCODE -ne 0) { throw "Launcher build failed with exit code $LASTEXITCODE." }
Copy-Item -LiteralPath $launcher -Destination $rootLauncher -Force
Write-Output $rootLauncher
