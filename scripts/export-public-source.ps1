[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Destination,
    [switch]$InitializeGit
)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
. (Join-Path $PSScriptRoot "PublicSource.ps1")
$root = Get-ProjectBroomRoot
$resolvedDestination = [IO.Path]::GetFullPath($Destination)
if ($resolvedDestination.StartsWith([IO.Path]::GetFullPath($root), [StringComparison]::OrdinalIgnoreCase)) {
    throw "Public export must be a sibling or external directory, not inside the development workspace."
}
if (Test-Path -LiteralPath $resolvedDestination) {
    if ((Get-ChildItem -LiteralPath $resolvedDestination -Force | Select-Object -First 1)) {
        throw "Destination exists and is not empty: $resolvedDestination"
    }
} else {
    New-Item -ItemType Directory -Path $resolvedDestination | Out-Null
}

foreach ($file in Get-ProjectBroomPublicSourceFiles $root) {
    $relative = Get-ProjectBroomRelativePath $root $file.FullName
    $target = Join-Path $resolvedDestination $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $target
}

if ($InitializeGit) {
    $git = Resolve-ProjectBroomCommand "git.exe" "Install Git for Windows."
    Invoke-ProjectBroomCommand $git -Arguments @("-C", $resolvedDestination, "init", "-b", "main")
}

Write-Output "Curated Project Broom source exported to $resolvedDestination"
Write-Output "Review it, run scripts\audit-public-tree.ps1, then create the initial commit."
