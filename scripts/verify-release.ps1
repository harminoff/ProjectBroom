[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$ReleaseDirectory)

. (Join-Path $PSScriptRoot "ProjectBroom.Common.ps1")
$release = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
$runtimeZips = @(Get-ChildItem -LiteralPath $release -Filter "ProjectBroom-Windows-x64-*.zip")
$sourceZips = @(Get-ChildItem -LiteralPath $release -Filter "ProjectBroom-Source-*.zip")
if ($runtimeZips.Count -ne 1) { throw "Expected exactly one Windows runtime archive; found $($runtimeZips.Count)." }
if ($sourceZips.Count -ne 1) { throw "Expected exactly one source archive; found $($sourceZips.Count)." }
$runtimeZip = $runtimeZips[0]
$sourceZip = $sourceZips[0]
$checksums = Join-Path $release "SHA256SUMS.txt"
if (-not (Test-Path -LiteralPath $checksums -PathType Leaf)) { throw "SHA256SUMS.txt is missing." }

$expected = @{}
foreach ($line in Get-Content -LiteralPath $checksums) {
    if ($line -match '^([0-9a-f]{64})  (.+)$') { $expected[$Matches[2]] = $Matches[1] }
}
foreach ($archive in @($runtimeZip, $sourceZip)) {
    $actual = Get-ProjectBroomSha256 $archive.FullName
    if ($expected[$archive.Name] -ne $actual) { throw "Checksum mismatch for $($archive.Name)." }
}

$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("ProjectBroom-release-verify-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null
try {
    Expand-Archive -LiteralPath $runtimeZip.FullName -DestinationPath (Join-Path $tempRoot "runtime")
    Expand-Archive -LiteralPath $sourceZip.FullName -DestinationPath (Join-Path $tempRoot "source")
    $manifestPaths = @(Get-ChildItem (Join-Path $tempRoot "runtime") -Filter "release-manifest.json" -Recurse)
    if ($manifestPaths.Count -ne 1) { throw "Expected exactly one release manifest; found $($manifestPaths.Count)." }
    $manifestPath = $manifestPaths[0]
    $manifest = Get-Content -Raw -LiteralPath $manifestPath.FullName | ConvertFrom-Json
    $packageRoot = Split-Path -Parent $manifestPath.FullName
    foreach ($file in $manifest.files) {
        $path = Join-Path $packageRoot $file.path
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Manifest file missing: $($file.path)" }
        if ((Get-ProjectBroomSha256 $path) -ne $file.sha256) { throw "Manifest hash mismatch: $($file.path)" }
    }
    foreach ($required in @("ProjectBroom.exe", "runtime\engine\gzdoom.exe", "runtime\engine\brogue-bridge.dll", "runtime\engine\openal32.dll", "runtime\engine\sndfile.dll", "runtime\engine\zmusic.dll", "runtime\brogue\brogue.exe", "runtime\compiler\ProjectBroomMapCompiler.exe", "runtime\iwad\freedoom2.wad", "game\ProjectBroom.pk3")) {
        if (-not (Test-Path -LiteralPath (Join-Path $packageRoot $required) -PathType Leaf)) { throw "Release component missing: $required" }
    }
    $forbidden = Get-ChildItem $tempRoot -Recurse -Force | Where-Object { $_.FullName -match '(reference-wads|cchest4\.wad|sunlust\.wad|CrashReport|\\generated\\|\\artifacts\\)' }
    if ($forbidden) { throw "Forbidden development/reference content was packaged: $($forbidden[0].FullName)" }
    $sourceRoot = Get-ChildItem (Join-Path $tempRoot "source") -Filter "README.md" -Recurse | Where-Object { $_.FullName -notmatch 'third_party_source' } | Select-Object -First 1
    if (-not $sourceRoot) { throw "Corresponding source README is missing." }
    if (-not (Get-ChildItem (Join-Path $tempRoot "source") -Filter "g_game.cpp" -Recurse | Where-Object { $_.FullName -match 'third_party_source' })) {
        throw "Patched GZDoom corresponding source is missing."
    }
} finally {
    $resolvedTemp = [IO.Path]::GetFullPath($tempRoot)
    $systemTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($systemTemp, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
Write-Output "Release verification passed."
