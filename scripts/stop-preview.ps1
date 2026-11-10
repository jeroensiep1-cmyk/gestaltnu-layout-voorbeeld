$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'preview-lib.ps1')

Write-PreviewLog '=== stop-preview ==='
Stop-PreviewListeners

if (Test-PreviewHealth) {
  Write-PreviewLog 'WARNING: something still answers on 8765 after stop.'
  exit 1
}

Write-PreviewLog 'Preview stopped. Port 8765 is free.'
Write-Host 'Preview gestopt. Poort 8765 is vrij.'
