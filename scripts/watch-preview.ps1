param(
  [Parameter(Mandatory = $true)]
  [string]$Root,
  [int]$IntervalSec = 5,
  [int]$FailLimit = 2
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'preview-lib.ps1')

$Root = (Resolve-Path -LiteralPath $Root).Path
Write-PreviewLog "Watchdog running for root=$Root interval=${IntervalSec}s"
$fails = 0

while ($true) {
  Start-Sleep -Seconds $IntervalSec

  if (Test-PreviewHealth) {
    $fails = 0
    continue
  }

  $fails++
  Write-PreviewLog "Watchdog health miss $fails/$FailLimit"

  if ($fails -lt $FailLimit) { continue }

  Write-PreviewLog 'Watchdog restarting preview server'
  # Stop server process only; keep this watchdog alive.
  if (Test-Path -LiteralPath $script:PidFile) {
    $raw = (Get-Content -LiteralPath $script:PidFile -Raw).Trim()
    if ($raw -match '^\d+$') {
      Stop-Process -Id ([int]$raw) -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $script:PidFile -Force -ErrorAction SilentlyContinue
  }

  Get-NetTCPConnection -LocalPort $script:PreviewPort -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    Where-Object { $_ -and $_ -gt 4 -and $_ -ne $PID } |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

  Start-Sleep -Milliseconds 500
  # Prefer PowerShell: full-file reads; avoids truncated large PNGs seen with python -m http.server.
  $proc = Start-PowerShellPreview -Root $Root
  if (-not $proc) { $proc = Start-PythonPreview -Root $Root }

  if (Wait-PreviewReady -TimeoutSec 12) {
    Write-PreviewLog "Watchdog restart OK pid=$($proc.Id)"
    $fails = 0
  } else {
    Write-PreviewLog 'Watchdog restart FAILED'
  }
}
