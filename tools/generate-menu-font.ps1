[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $projectRoot "mod\BrogueDoom\graphics\fonts\ui"
$outputRoot = Join-Path $projectRoot "mod\BrogueDoom\graphics\fonts\menu"
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

foreach ($codepoint in 33..126) {
    $name = "BFU{0:D3}.png" -f $codepoint
    $sourcePath = Join-Path $sourceRoot $name
    $outputPath = Join-Path $outputRoot ("BFT{0:D3}.png" -f $codepoint)
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Missing Brogue UI glyph: $sourcePath"
    }

    $source = [System.Drawing.Bitmap]::FromFile($sourcePath)
    $target = New-Object System.Drawing.Bitmap($source.Width, $source.Height,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        for ($y = 0; $y -lt $source.Height; $y++) {
            for ($x = 0; $x -lt $source.Width; $x++) {
                $pixel = $source.GetPixel($x, $y)
                $alpha = if ($pixel.A -ge 42) { 255 } else { 0 }
                $target.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($alpha, 255, 255, 255))
            }
        }
        $target.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $target.Dispose()
        $source.Dispose()
    }
}

Write-Output "Generated crisp Brogue menu glyphs in $outputRoot"
