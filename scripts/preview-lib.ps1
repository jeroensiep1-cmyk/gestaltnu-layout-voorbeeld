# Shared helpers for Gestalt Nu local preview on port 8765.

$ErrorActionPreference = 'Stop'

$script:PreviewPort = 8765
$script:PreviewBind = '127.0.0.1'
$script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script:DefaultRoot = Join-Path $script:RepoRoot 'site'
$script:PidFile = Join-Path $env:TEMP 'gestaltnu-preview-8765.pid'
$script:WatchPidFile = Join-Path $env:TEMP 'gestaltnu-preview-8765-watch.pid'
$script:LogFile = Join-Path $env:TEMP 'gestaltnu-preview-8765.log'
$script:ReadyFile = Join-Path $env:TEMP 'gestaltnu-preview-8765.ready'

function Write-PreviewLog([string]$Message) {
  $line = '{0:u} {1}' -f (Get-Date), $Message
  Add-Content -LiteralPath $script:LogFile -Value $line -Encoding UTF8
  Write-Host $line
}

function Get-RealPython {
  $candidates = @(
    "$env:LocalAppData\Programs\Python\Python312\python.exe",
    "$env:LocalAppData\Programs\Python\Python313\python.exe",
    "$env:LocalAppData\Programs\Python\Python311\python.exe",
    'C:\Python312\python.exe',
    'C:\Python313\python.exe'
  )
  foreach ($path in $candidates) {
    if (Test-Path -LiteralPath $path) { return $path }
  }

  foreach ($name in @('py', 'python')) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    $src = $cmd.Source
    if ($src -match 'WindowsApps') { continue }
    try {
      $probe = & $src -c "import sys; print(sys.executable)" 2>$null
      if ($LASTEXITCODE -eq 0 -and $probe -and ($probe -notmatch 'WindowsApps')) {
        return $probe.Trim()
      }
    } catch {}
  }
  return $null
}

function Test-PreviewHealth {
  try {
    $resp = Invoke-WebRequest -Uri ("http://{0}:{1}/" -f $script:PreviewBind, $script:PreviewPort) -UseBasicParsing -TimeoutSec 3
    return ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500)
  } catch {
    return $false
  }
}

function Stop-PreviewListeners {
  # Stop tracked PIDs first.
  foreach ($file in @($script:WatchPidFile, $script:PidFile)) {
    if (-not (Test-Path -LiteralPath $file)) { continue }
    $raw = (Get-Content -LiteralPath $file -Raw).Trim()
    if ($raw -match '^\d+$') {
      $procId = [int]$raw
      if ($procId -gt 0) {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Write-PreviewLog "Stopped tracked PID $procId from $(Split-Path $file -Leaf)"
      }
    }
    Remove-Item -LiteralPath $file -Force -ErrorAction SilentlyContinue
  }

  # Kill anything whose command line clearly owns our preview.
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.CommandLine -and (
        $_.CommandLine -match 'gestaltnu-preview|gn-http8765|http\.server.*8765|PreviewPort.*8765'
      )
    } |
    ForEach-Object {
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
      Write-PreviewLog "Stopped related process $($_.ProcessId)"
    }

  # Last resort: owners of TCP 8765 (never kill System/pid 4).
  Get-NetTCPConnection -LocalPort $script:PreviewPort -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    Where-Object { $_ -and $_ -gt 4 } |
    ForEach-Object {
      Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
      Write-PreviewLog "Stopped port owner PID $_"
    }

  Remove-Item -LiteralPath $script:ReadyFile -Force -ErrorAction SilentlyContinue
  Start-Sleep -Milliseconds 400
}

function Start-PythonPreview([string]$Root) {
  $python = Get-RealPython
  if (-not $python) { return $null }

  # Note: Python's http.server has truncated large hero PNGs (~8MB) mid-response
  # in this environment. Prefer PowerShell unless explicitly requested.
  $argList = @(
    '-m', 'http.server', "$script:PreviewPort",
    '--bind', $script:PreviewBind,
    '--directory', $Root
  )
  $proc = Start-Process -FilePath $python -ArgumentList $argList -WindowStyle Hidden -PassThru
  Set-Content -LiteralPath $script:PidFile -Value $proc.Id -Encoding ASCII
  Write-PreviewLog "Started Python server PID $($proc.Id) ($python) root=$Root"
  return $proc
}

function Start-PowerShellPreview([string]$Root) {
  $serverScript = Join-Path $PSScriptRoot 'preview-server.ps1'
  $proc = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass',
    '-File', $serverScript,
    '-Root', $Root,
    '-Port', "$script:PreviewPort",
    '-Bind', $script:PreviewBind
  ) -WindowStyle Hidden -PassThru
  Set-Content -LiteralPath $script:PidFile -Value $proc.Id -Encoding ASCII
  Write-PreviewLog "Started PowerShell server PID $($proc.Id) root=$Root"
  return $proc
}

function Wait-PreviewReady([int]$TimeoutSec = 10) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-PreviewHealth) { return $true }
    Start-Sleep -Milliseconds 250
  }
  return $false
}
