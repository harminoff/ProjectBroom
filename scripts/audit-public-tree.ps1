[CmdletBinding()]
param([switch]$WorkingTree)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
. (Join-Path $PSScriptRoot "PublicSource.ps1")
$root = Get-ProjectBroomRoot
$errors = [Collections.Generic.List[string]]::new()

if ($WorkingTree) {
    $files = @(Get-ProjectBroomPublicSourceFiles $root)
} else {
    $git = Resolve-ProjectBroomCommand "git.exe" "Install Git for Windows."
    $tracked = & $git -C $root ls-files
    $files = @($tracked | ForEach-Object { Get-Item -LiteralPath (Join-Path $root $_) })
}

$forbiddenRoots = @("artifacts/", "generated/", "tooling/", "crash-analysis/", ".deps/", ".build/")
foreach ($file in $files) {
    $relative = (Get-ProjectBroomRelativePath $root $file.FullName).Replace('\', '/')
    if ($forbiddenRoots | Where-Object { $relative.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }) {
        $errors.Add("Forbidden publication path: $relative")
    }
    if ($file.Length -gt 50MB) { $errors.Add("Tracked/public file exceeds 50 MiB: $relative ($($file.Length) bytes)") }
    if ($relative -match '\.(exe|dll|pdb|ilk|lib|exp|zip|7z|wad)$') {
        $errors.Add("Build, archive, or WAD binary must be a release/dependency artifact: $relative")
    }
    if ($file.Extension -in @('.md', '.txt', '.json', '.yml', '.yaml', '.ps1', '.py', '.cs', '.cpp', '.h')) {
        $text = Get-Content -Raw -LiteralPath $file.FullName -ErrorAction SilentlyContinue
        if ($text -match 'C:\\Temp\\BrogueDoom2|C:\\Users\\harmi') {
            $errors.Add("Machine-specific absolute path in $relative")
        }
    }
}

foreach ($required in @("README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "dependencies.lock.json")) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $required) -PathType Leaf)) { $errors.Add("Missing required public file: $required") }
}

try { $null = Get-Content -Raw -LiteralPath (Join-Path $root "dependencies.lock.json") | ConvertFrom-Json }
catch { $errors.Add("dependencies.lock.json is invalid JSON: $($_.Exception.Message)") }

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}
Write-Output "Public-source audit passed for $($files.Count) files."
