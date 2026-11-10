# UTF-8 veilig openen van de bioscoop-preview (ASCII-paden only).
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$html = Join-Path $root "hero-bioscoop-voorbeeld.html"
$png  = Join-Path $root "bioscoop-doodle-final.png"

if (-not (Test-Path -LiteralPath $png)) {
  Write-Error "Eindbestand ontbreekt: $png"
  exit 1
}
if (-not (Test-Path -LiteralPath $html)) {
  Write-Error "Preview ontbreekt: $html"
  exit 1
}

# Geen bestanden met accenten (zoals scène) in het pad gebruiken.
Invoke-Item -LiteralPath $html
Write-Host "opened $html"
exit 0
