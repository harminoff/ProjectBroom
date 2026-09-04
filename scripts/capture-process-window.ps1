[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [int]$ProcessId,
    [Parameter(Mandatory)]
    [string]$OutputPath
)

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;

public static class BrogueCaptureWindow {
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr parameter);

    [StructLayout(LayoutKind.Sequential)]
    public struct Rect { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr parameter);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint processId);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hwnd, out Rect rect);
}
'@

$script:capturedWindow = [IntPtr]::Zero
$callback = [BrogueCaptureWindow+EnumWindowsProc] {
    param([IntPtr]$handle, [IntPtr]$unused)
    [uint32]$owner = 0
    [BrogueCaptureWindow]::GetWindowThreadProcessId($handle, [ref]$owner) | Out-Null
    if ($owner -eq $ProcessId -and [BrogueCaptureWindow]::IsWindowVisible($handle)) {
        $script:capturedWindow = $handle
        return $false
    }
    return $true
}
[BrogueCaptureWindow]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
$window = $script:capturedWindow
if ($window -eq [IntPtr]::Zero) {
    $window = (Get-Process -Id $ProcessId -ErrorAction Stop).MainWindowHandle
}
if ($window -eq [IntPtr]::Zero) { throw "No visible window belongs to process $ProcessId." }

$rect = New-Object BrogueCaptureWindow+Rect
if (-not [BrogueCaptureWindow]::GetWindowRect($window, [ref]$rect)) {
    throw "Could not read the window bounds for process $ProcessId."
}
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $resolved = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($resolved)) | Out-Null
    $bitmap.Save($resolved, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $resolved
} finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}
