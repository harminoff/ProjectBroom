[CmdletBinding()]
param(
    [string]$RepositoryName = "ProjectBroom",
    [string]$Destination = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "ProjectBroom-public"),
    [switch]$CreatePrivateRemote
)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$root = Get-ProjectBroomRoot
$destinationPath = [IO.Path]::GetFullPath($Destination)

& (Join-Path $PSScriptRoot "audit-public-tree.ps1") -WorkingTree
& (Join-Path $PSScriptRoot "export-public-source.ps1") -Destination $destinationPath -InitializeGit

$git = Resolve-ProjectBroomCommand "git.exe" "Install Git for Windows."
Invoke-ProjectBroomCommand $git -Arguments @("-C", $destinationPath, "add", "--all")
Write-Output "Curated source is staged at $destinationPath. Review 'git status' and 'git diff --cached' before committing."

if ($CreatePrivateRemote) {
    $gh = Resolve-ProjectBroomCommand "gh.exe" "Install GitHub CLI and authenticate with 'gh auth login'."
    $status = & $git -C $destinationPath status --porcelain
    if ($status) {
        throw "Create and review the initial commit in $destinationPath before creating the remote."
    }
    Invoke-ProjectBroomCommand $gh -Arguments @("repo", "create", $RepositoryName, "--private", "--source", $destinationPath, "--remote", "origin", "--push", "--description", "Brogue CE as the authoritative game simulation, presented through a 3D UZDoom frontend.")
    Invoke-ProjectBroomCommand $gh -Arguments @("repo", "edit", $RepositoryName, "--enable-issues", "--enable-discussions", "--enable-wiki=false", "--delete-branch-on-merge", "--enable-merge-commit=false", "--enable-rebase-merge=false", "--enable-squash-merge")
}
