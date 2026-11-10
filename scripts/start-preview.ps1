param(
  [string]$Root = '',
  [ValidateSet('auto', 'powershell', 'python')]
  [string]$Engine = 'powershell',
  [switch]$NoWatchdog,
  [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'preview-lib.ps1')

if (-not $Root) { $Root = $script:DefaultRoot }
$Root = (Resolve-Path -LiteralPath $Root).Path

Write-PreviewLog "=== start-preview root=$Root engine=$Engine ==="
Stop-PreviewListeners

# Default: PowerShell. Python http.server truncated voorpagina-origineel.png (~8MB) here.
$proc = $null
$engine = $Engine
if ($Engine -eq 'python' -or $Engine -eq 'auto') {
  $proc = Start-PythonPreview -Root $Root
  if ($proc) { $engine = 'python' }
}
if (-not $proc) {
  if ($Engine -eq 'python') {
    Write-PreviewLog 'Python requested but unavailable; falling back to PowerShell.'
  }
  $proc = Start-PowerShellPreview -Root $Root
  $engine = 'powershell'
}

if (-not (Wait-PreviewReady -TimeoutSec 12)) {
  Write-PreviewLog 'ERROR: preview did not become healthy within 12s.'
  if (Test-Path -LiteralPath $script:LogFile) {
    Get-Content -LiteralPath $script:LogFile -Tail 20 | ForEach-Object { Write-Host $_ }
  }
  throw "Preview on http://$($script:PreviewBind):$($script:PreviewPort)/ failed to start."
}

Set-Content -LiteralPath $script:ReadyFile -Value ("ok engine={0} pid={1} root={2}" -f $engine, $proc.Id, $Root) -Encoding UTF8
Write-PreviewLog "Healthy on http://$($script:PreviewBind):$($script:PreviewPort)/ (engine=$engine pid=$($proc.Id))"

if (-not $NoWatchdog) {
  $watch = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass',
    '-File', (Join-Path $PSScriptRoot 'watch-preview.ps1'),
    '-Root', $Root
  ) -WindowStyle Hidden -PassThru
  Set-Content -LiteralPath $script:WatchPidFile -Value $watch.Id -Encoding ASCII
  Write-PreviewLog "Watchdog started PID $($watch.Id)"
}

if ($OpenBrowser) {
  Start-Process ("http://{0}:{1}/" -f $script:PreviewBind, $script:PreviewPort)
}

Write-Host ""
Write-Host "Preview: http://$($script:PreviewBind):$($script:PreviewPort)/"
Write-Host "Stop with:  .\scripts\stop-preview.ps1"
Write-Host "Log:        $script:LogFile"
