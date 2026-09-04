Set-StrictMode -Version Latest

function Get-ProjectBroomPublicSourceFiles([string]$Root) {
    $rootFiles = @(
        ".editorconfig", ".gitattributes", ".gitignore", "AGENTS.md",
        "ASSETS-LICENSE.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md",
        "dependencies.lock.json", "LICENSE", "README.md", "SECURITY.md",
        "SUPPORT.md", "THIRD_PARTY_NOTICES.md"
    )
    $sourceRoots = @(".github", "assets", "docs", "mod", "patches", "scripts", "src", "tools")
    $files = @()
    foreach ($name in $rootFiles) {
        $path = Join-Path $Root $name
        if (Test-Path -LiteralPath $path -PathType Leaf) { $files += Get-Item -LiteralPath $path }
    }
    foreach ($name in $sourceRoots) {
        $path = Join-Path $Root $name
        if (Test-Path -LiteralPath $path -PathType Container) {
            $files += Get-ChildItem -LiteralPath $path -File -Recurse
        }
    }

    $excluded = @(
        '(^|/)(obj|build|build-[^/]+|__pycache__|\.vs|\.idea)(/|$)',
        '^tools/BrogueDoomLauncher/bin/',
        '^src/brogue-mapgen/bin/(?!assets/)',
        '^src/brogue-mapgen/vars/',
        '^docs/cc4-',
        '^assets/terrain/cc4_cave_registry\.json$',
        '^tools/(analyze_reference_wads|render_cc4_.+|test_cc4_resources|verify_cc4_matrix|wadlib)\.py$',
        '\.(exe|dll|pdb|ilk|lib|exp|o|a|pyc|zip|7z|wad)$',
        '(^|/)(CrashReport|BrogueRunHistory)'
    )
    return $files | Where-Object {
        $relative = (Get-ProjectBroomRelativePath $Root $_.FullName).Replace('\', '/')
        -not ($excluded | Where-Object { $relative -match $_ })
    } | Sort-Object FullName -Unique
}
