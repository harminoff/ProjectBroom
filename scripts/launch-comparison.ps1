[CmdletBinding()]
param(
    [ValidateRange(1, [int]::MaxValue)]
    [int]$Seed = 1,
    [ValidateRange(1.0, 3.0)]
    [double]$HudScale = 1.0,
    [switch]$ShowFPS
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceLauncher = Join-Path $PSScriptRoot "launch-source-bridge.ps1"
$brogueDir = Join-Path $projectRoot "tooling\BrogueCE-compare\source-7f52dd9\bin"
$brogueExe = Join-Path $brogueDir "brogue.exe"
$expectedBrogueHash = "fedacd18f475a2f9c702166b2b3193371e0498953675826b74ba53b019d9512b"

foreach ($required in @(
    $sourceLauncher,
    $brogueExe,
    (Join-Path $brogueDir "SDL2.dll"),
    (Join-Path $brogueDir "SDL2_image.dll"),
    (Join-Path $brogueDir "assets\tiles.bin"),
    (Join-Path $brogueDir "keymap.txt")
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required comparison artifact is missing: $required"
    }
}

$actualBrogueHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $brogueExe).Hash.ToLowerInvariant()
if ($actualBrogueHash -ne $expectedBrogueHash) {
    throw "Pinned comparison Brogue hash mismatch. Expected $expectedBrogueHash, got $actualBrogueHash."
}

Add-Type -AssemblyName System.Windows.Forms
if (-not ("BrogueDoom.NativeWindow" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
namespace BrogueDoom {
    public static class NativeWindow {
        [DllImport("user32.dll", SetLastError=true)]
        public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int width, int height, uint flags);
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int command);
    }
}
"@
}

function Wait-MainWindow([System.Diagnostics.Process]$Process, [int]$TimeoutMilliseconds = 20000) {
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
    do {
        if ($Process.HasExited) {
            throw "Process $($Process.Id) exited before creating a window."
        }
        $Process.Refresh()
        if ($Process.MainWindowHandle -ne [IntPtr]::Zero) {
            return $Process.MainWindowHandle
        }
        Start-Sleep -Milliseconds 100
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Timed out waiting for process $($Process.Id) to create a window."
}

$workingArea = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$halfWidth = [Math]::Floor($workingArea.Width / 2)
$windowHeight = $workingArea.Height
$brogue = $null
$doom = $null

try {
    $brogue = Start-Process -FilePath $brogueExe -WorkingDirectory $brogueDir -ArgumentList @("--seed", $Seed) -PassThru
    $brogueWindow = Wait-MainWindow $brogue

    $launchOutput = & $sourceLauncher -Seed $Seed -WindowWidth $halfWidth -WindowHeight $windowHeight -ComparePid $brogue.Id -HudScale $HudScale -ShowFPS:$ShowFPS -PassThru
    $doom = $launchOutput | Where-Object { $_ -is [System.Diagnostics.Process] } | Select-Object -Last 1
    if ($null -eq $doom) {
        throw "The GZDoom launcher did not return its process handle."
    }
    $doomWindow = Wait-MainWindow $doom

    [BrogueDoom.NativeWindow]::ShowWindow($brogueWindow, 9) | Out-Null
    [BrogueDoom.NativeWindow]::ShowWindow($doomWindow, 9) | Out-Null
    [BrogueDoom.NativeWindow]::SetWindowPos($brogueWindow, [IntPtr]::Zero, $workingArea.Left, $workingArea.Top, $halfWidth, $windowHeight, 0x0040) | Out-Null
    [BrogueDoom.NativeWindow]::SetWindowPos($doomWindow, [IntPtr]::Zero, $workingArea.Left + $halfWidth, $workingArea.Top, $workingArea.Width - $halfWidth, $windowHeight, 0x0040) | Out-Null
    [BrogueDoom.NativeWindow]::SetForegroundWindow($brogueWindow) | Out-Null

    Write-Output "Comparison mode started for exact pinned Brogue seed $Seed."
    Write-Output "Brogue PID $($brogue.Id) is on the left; GZDoom PID $($doom.Id) is on the right."
    Write-Output "Numpad 8/9/6/3/2/1/4/7 moves both simulations; Numpad 5 waits. Press each key once."
} catch {
    if ($null -ne $doom -and -not $doom.HasExited) { Stop-Process -Id $doom.Id -Force }
    if ($null -ne $brogue -and -not $brogue.HasExited) { Stop-Process -Id $brogue.Id -Force }
    throw
}
