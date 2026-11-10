param(
  [Parameter(Mandatory = $true)]
  [string]$Root,
  [int]$Port = 8765,
  [string]$Bind = '127.0.0.1'
)

$ErrorActionPreference = 'Stop'
$readyFile = Join-Path $env:TEMP 'gestaltnu-preview-8765.ready'
$logFile = Join-Path $env:TEMP 'gestaltnu-preview-8765.log'

function Write-Log([string]$msg) {
  Add-Content -LiteralPath $logFile -Value (('{0:u} {1}' -f (Get-Date), $msg)) -Encoding UTF8
}

function Get-ContentType([string]$path) {
  switch -Regex ([IO.Path]::GetExtension($path).ToLowerInvariant()) {
    '\.html?' { 'text/html; charset=utf-8'; break }
    '\.css'   { 'text/css; charset=utf-8'; break }
    '\.js'    { 'application/javascript; charset=utf-8'; break }
    '\.json'  { 'application/json; charset=utf-8'; break }
    '\.svg'   { 'image/svg+xml'; break }
    '\.png'   { 'image/png'; break }
    '\.jpe?g' { 'image/jpeg'; break }
    '\.webp'  { 'image/webp'; break }
    '\.gif'   { 'image/gif'; break }
    '\.md'    { 'text/plain; charset=utf-8'; break }
    '\.txt'   { 'text/plain; charset=utf-8'; break }
    '\.webmanifest' { 'application/manifest+json'; break }
    default   { 'application/octet-stream' }
  }
}

function Send-Bytes($ctx, [byte[]]$bytes, [string]$contentType, [int]$status = 200) {
  $ctx.Response.StatusCode = $status
  $ctx.Response.ContentType = $contentType
  $ctx.Response.Headers['Cache-Control'] = 'no-store'
  # Use explicit int count — PowerShell + HttpListener mismatch on Length/LongLength
  # caused Content-Length errors on large PNGs (~8MB hero), blanking the homepage.
  $count = [int]$bytes.LongLength
  $ctx.Response.ContentLength64 = $count
  $ctx.Response.OutputStream.Write($bytes, 0, $count)
  $ctx.Response.Close()
}

function Send-File($ctx, [string]$path, [string]$contentType, [int]$status = 200) {
  $len = [long](Get-Item -LiteralPath $path).Length
  $ctx.Response.StatusCode = $status
  $ctx.Response.ContentType = $contentType
  $ctx.Response.Headers['Cache-Control'] = 'no-store'
  $ctx.Response.ContentLength64 = $len
  $fs = [IO.File]::OpenRead($path)
  try {
    $fs.CopyTo($ctx.Response.OutputStream)
  } finally {
    $fs.Dispose()
    $ctx.Response.Close()
  }
}

function Send-Text($ctx, [string]$text, [string]$contentType, [int]$status = 200) {
  Send-Bytes $ctx ([Text.Encoding]::UTF8.GetBytes($text)) $contentType $status
}

if (-not (Test-Path -LiteralPath $Root)) { throw "Root not found: $Root" }

$prefix = "http://${Bind}:${Port}/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
$listener.Start()
Set-Content -LiteralPath $readyFile -Value ("ok pid={0} root={1}" -f $PID, $Root) -Encoding UTF8
Write-Log "listening $prefix root=$Root pid=$PID"

while ($listener.IsListening) {
  $ctx = $null
  try {
    $ctx = $listener.GetContext()
    $rawPath = [Uri]::UnescapeDataString($ctx.Request.Url.LocalPath)
    $rel = $rawPath.TrimStart('/').Replace('/', [IO.Path]::DirectorySeparatorChar)

    if ([string]::IsNullOrWhiteSpace($rel)) {
      $index = Join-Path $Root 'index.html'
      if (Test-Path -LiteralPath $index -PathType Leaf) {
        Send-File $ctx $index 'text/html; charset=utf-8' 200
        Write-Log '200 / -> index.html'
        continue
      }
      $names = @(Get-ChildItem -LiteralPath $Root -File | Sort-Object Name)
      $items = foreach ($f in $names) {
        $href = '/' + [Uri]::EscapeDataString($f.Name)
        "<li><a href=`"$href`">$([System.Net.WebUtility]::HtmlEncode($f.Name))</a></li>"
      }
      $html = "<!doctype html><html lang=`"nl`"><meta charset=`"utf-8`"><title>Preview $Port</title><body><h1>Preview $Port</h1><ul>$($items -join '')</ul></body></html>"
      Send-Text $ctx $html 'text/html; charset=utf-8' 200
      continue
    }

    $full = [IO.Path]::GetFullPath((Join-Path $Root $rel))
    $rootFull = [IO.Path]::GetFullPath($Root)
    if (-not $full.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)) {
      Send-Text $ctx 'Forbidden' 'text/plain; charset=utf-8' 403
      continue
    }

    if ((Test-Path -LiteralPath $full -PathType Container)) {
      $index = Join-Path $full 'index.html'
      if (Test-Path -LiteralPath $index -PathType Leaf) {
        Send-File $ctx $index 'text/html; charset=utf-8' 200
        continue
      }
      Send-Text $ctx 'Not Found' 'text/plain; charset=utf-8' 404
      continue
    }

    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
      Send-Text $ctx 'Not Found' 'text/plain; charset=utf-8' 404
      continue
    }

    Send-File $ctx $full (Get-ContentType $full) 200
  }
  catch {
    Write-Log ("ERR " + $_.Exception.Message)
    if ($null -ne $ctx) {
      try { Send-Text $ctx 'Internal Server Error' 'text/plain; charset=utf-8' 500 } catch {}
    }
  }
}
