<#
.SYNOPSIS
  Generic project starter: inventory, group, dedupe, remove empty folders.

.DESCRIPTION
  Place this script in a project folder and run it. By default the project
  root is the folder that contains this script. Or pass -RootPath.

  Steps:
    1. Inventory folders and files
    2. Group loose root files neatly by type under _grouped\
    3. Find and remove duplicate files (SHA256)
    4. Delete empty folders

  Does not hardcode a specific project path.

  GOAL — BEST WEBSITE / #1 FINDABILITY:
  The user's aim is to create the best website in the world: the most
  easily readable by Google and by AI, so it ranks number one in both
  Google and AI search results. Folder/file cleanup with this script
  supports a clear, organized starting point for that work — it does
  not rewrite live site content by itself.

  AGENT STANCE — CURIOUS AND LEARNING:
  The agent should be curious and always learning from itself. No excuses.
  Take the time needed. When new market developments appear (SEO, AI
  search, web craft, accessibility, performance), check them. Once the
  website is live, stay curious and proactively suggest concrete
  additions or improvements — without changing the live site until the
  user explicitly asks.

  AGENT STANCE — PERFECTIONATE (EVEN IF ANNOYING):
  Push quality to the point of being annoying: double-check, dig deeper,
  and polish until it is truly solid. Before saying no, thoroughly search
  yourself first — other paths, tools, workarounds, sources — and only
  say no when that has genuinely been exhausted. A quick no is not enough.

  SAFETY — LIVE WEBSITE (hard rule):
  Until the user has EXPLICITLY said they are working on the live version
  (pass -AllowLiveSite only after that clear go-ahead), this script must
  NEVER modify, move, overwrite, or delete anything under the live site
  folder, especially index.html and bericht.js:
    C:\Users\jeroe\gestaltnu-layout-voorbeeld\site
  Inventory may still list that folder; only write actions are blocked.
  Without -AllowLiveSite, only non-live files may be changed.

  VISUAL STYLE — POPPETJES / DOODLES:
  Website figures start from Open Doodles as a base, then become original
  Gestalt Nu poppetjes in the team's own style. Existing creations that
  belong to this style include: the group / circle with the chainsaw
  (groep / cirkel met de kettingzaag; e.g. figuren_v12 / groep-poppetjes),
  and the monnik-met-koe / monnik-koeien doodle line.

  STYLE BOARD (definitive):
  afbeeldingen\a-stijlblad.png is the definitive visual style reference
  (colors, lines, elements, type) — no longer "only a proposal".

  COLOR PALETTE (live site — site\stijl.css):
  --creme #f6eedf | --inkt #2a231c | --gedempt #5e564c |
  --teal #0f6e6e | --teal-donker #0b5555 | --terracotta #c45c3e
  (Illustration board may list extra greens/peach/yellow; live CSS is
  the shorter site palette above.)

  FUTURE WEBSITE WRITING — INPUTS:
  When writing site text: (a) use the Google Keep thought-process
  overview from 3 November 2026
  (experimenten\gestalt-nu-Grok\keep-notities-overzicht.md);
  (b) match the personal writing style of the live site under
  C:\Users\jeroe\gestaltnu-layout-voorbeeld\site. Do not invent a
  different corporate voice.

  LATER PROJECT — SOLO VIBES:
  Separate idea for later: Solo Vibes — loneliness / being alone
  (alleen en eenzaamheid): personal + community, recognition, from
  FOMO to JOMO. May also appear in Keep. Do not start unless asked.

  CORE PRINCIPLE — ESSENCE (Gestalt Nu):
  No labels, no mandatory paperwork. Stay at the essence. Personal
  approach — not tied to insurance or GGZ systems.

  ACCESSIBILITY — USER IS DYSLEXIC:
  The user is dyslexic. The agent must do as much writing as possible
  itself. Put anything the user needs (paths, code, instructions) into
  the chat as a link or plain copy-pasteable text — do not rely on
  reading long paths or code aloud.

  STORAGE — GESTALT NU CURSOR (desktop):
  All future work (images, marketing, new website projects, etc.) must
  be stored under the desktop folder Gestalt Nu Cursor, in the correct
  subfolders (e.g. afbeeldingen, marketing, nieuwe website, and any
  new project folders the user created in the sidebar):
    C:\Users\jeroe\OneDrive\Bureaublad\Gestalt Nu Cursor
  Do not dump outputs elsewhere on the desktop. Do not rename or move
  the Gestalt Nu Cursor folder itself. Canonical live site code remains
  under gestaltnu-layout-voorbeeld\site unless the user says otherwise.

  AGENT STANCE — SELF-REFLECTION BEFORE PRESENTING:
  Always review your own work before presenting it. Check whether
  everything discussed in the conversation is included. Never rely on
  the user to point out missing items — proactively find gaps and fill
  them yourself. Never repeat mistakes. Keep learning from every
  conversation. Treat every user correction as a permanent lesson and
  store it in this script header (or the standing project rules) so it
  is not forgotten. After each task, ask yourself: did I miss anything
  the user mentioned?

  AGENT STANCE — STRICT NO EXCUSES:
  Never give excuses for being too fast, not doing things well, or not
  having enough time. Follow every user instruction exactly as written,
  even if the wording differs slightly from what was expected. No
  excuses. No shortcuts.

.EXAMPLE
  .\start-script.ps1
  .\start-script.ps1 -WhatIf
  .\start-script.ps1 -RootPath 'D:\Projects\nieuw'
#>

[CmdletBinding()]
param(
  [Parameter()]
  [string]$RootPath,

  [Parameter()]
  [switch]$WhatIf,

  # ONLY after the user explicitly said they are working on the live site.
  [Parameter()]
  [switch]$AllowLiveSite
)

$ErrorActionPreference = 'Stop'

if ($RootPath) {
  $Root = (Resolve-Path -LiteralPath $RootPath).Path
} else {
  $Root = $PSScriptRoot
  if (-not $Root) {
    $Root = (Get-Location).Path
  }
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$ReportDir = Join-Path $env:TEMP ("project-start-" + $stamp)
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ReportPath = Join-Path $ReportDir 'start-script-report.txt'

$ProtectedNames = @(
  '.git', '.cursor', '.vscode', '.idea',
  'node_modules', 'vendor', 'dist', 'build', 'out',
  'site', 'scripts', 'checkpoints',
  '_grouped', 'afbeeldingen', 'marketing', 'nieuwe website', 'experimenten'
)

$GroupMap = [ordered]@{
  'images'       = @('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.bmp', '.tif', '.tiff')
  'documents'    = @('.md', '.txt', '.pdf', '.doc', '.docx', '.rtf', '.odt')
  'spreadsheets' = @('.xls', '.xlsx', '.csv')
  'archives'     = @('.zip', '.7z', '.rar', '.tar', '.gz')
  'audio'        = @('.mp3', '.wav', '.m4a', '.flac', '.ogg')
  'video'        = @('.mp4', '.mov', '.avi', '.mkv', '.webm')
  'code'         = @('.ps1', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.yml', '.yaml', '.xml', '.sh', '.bat', '.cmd')
}

$KeepAtRoot = @(
  'AGENTS.md', 'README.md', 'LICENSE', 'LICENSE.md',
  '.gitignore', '.gitattributes'
)

# Canonical live website folder — off-limits unless -AllowLiveSite.
$LiveSitePath = 'C:\Users\jeroe\gestaltnu-layout-voorbeeld\site'
try {
  if (Test-Path -LiteralPath $LiveSitePath) {
    $LiveSitePath = (Resolve-Path -LiteralPath $LiveSitePath).Path
  }
} catch { }

$SelfName = Split-Path -Leaf $MyInvocation.MyCommand.Path
$Lines = New-Object System.Collections.Generic.List[string]

function Write-Report {
  param([string]$Message)
  [void]$Lines.Add($Message)
  Write-Host $Message
}

function Test-IsLiveSitePath {
  param([string]$FullPath)
  if (-not $FullPath) { return $false }
  $full = $FullPath
  try { $full = [IO.Path]::GetFullPath($FullPath) } catch { }
  $live = $LiveSitePath.TrimEnd('\', '/')
  if ($full.Equals($live, [StringComparison]::OrdinalIgnoreCase)) { return $true }
  $prefix = $live + [IO.Path]::DirectorySeparatorChar
  if ($full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { return $true }
  # Also treat "<root>\site\..." as live when root is the Gestalt workspace / junction.
  if ($FullPath.Length -gt $Root.Length) {
    $rel = $FullPath.Substring($Root.Length).TrimStart('\', '/')
    if ($rel -eq 'site' -or $rel.StartsWith('site\', [StringComparison]::OrdinalIgnoreCase) -or $rel.StartsWith('site/', [StringComparison]::OrdinalIgnoreCase)) {
      return $true
    }
  }
  return $false
}

function Test-IsProtectedPath {
  param([string]$FullPath)
  # Live site is always protected unless user explicitly allowed live work.
  if (-not $AllowLiveSite -and (Test-IsLiveSitePath -FullPath $FullPath)) { return $true }
  if ($FullPath.Length -le $Root.Length) { return $true }
  $rel = $FullPath.Substring($Root.Length).TrimStart('\', '/')
  if (-not $rel) { return $true }
  $first = ($rel -split '[\\/]')[0]
  if ($ProtectedNames -contains $first) { return $true }
  if ($first -eq $SelfName) { return $true }
  return $false
}

function Test-MayWritePath {
  param([string]$FullPath)
  if (-not $AllowLiveSite -and (Test-IsLiveSitePath -FullPath $FullPath)) {
    Write-Report ("  BLOCK live site  {0}" -f $FullPath)
    return $false
  }
  return $true
}

function Get-GroupName {
  param([string]$Extension)
  $ext = $Extension.ToLowerInvariant()
  foreach ($key in $GroupMap.Keys) {
    if ($GroupMap[$key] -contains $ext) { return $key }
  }
  return 'other'
}

Write-Report '=== Project start script ==='
Write-Report ("Root: {0}" -f $Root)
Write-Report ("Report: {0}" -f $ReportPath)
Write-Report ("WhatIf: {0}" -f [bool]$WhatIf)
Write-Report ("AllowLiveSite: {0}" -f [bool]$AllowLiveSite)
Write-Report ("Live site (protected): {0}" -f $LiveSitePath)
if (-not $AllowLiveSite) {
  Write-Report 'SAFETY: live site folder will not be modified, moved, overwritten, or deleted.'
}
Write-Report ''

if (-not $AllowLiveSite -and (Test-IsLiveSitePath -FullPath $Root)) {
  Write-Report 'ABORT: RootPath is the live site folder. Refusing to run without -AllowLiveSite.'
  $Lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8
  throw 'Live site root blocked. Pass -AllowLiveSite only after explicit user go-ahead.'
}

# ---------------------------------------------------------------------------
# 1) Inventory
# ---------------------------------------------------------------------------
Write-Report '=== 1) Inventory ==='
$allItems = @(Get-ChildItem -LiteralPath $Root -Force -Recurse -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and
    $_.FullName -notmatch '\\node_modules\\' -and
    $_.FullName -notmatch '\\\.cursor\\'
  })

$dirs  = @($allItems | Where-Object { $_.PSIsContainer })
$files = @($allItems | Where-Object { -not $_.PSIsContainer })

Write-Report ("Folders: {0}" -f $dirs.Count)
Write-Report ("Files:   {0}" -f $files.Count)
Write-Report 'Top-level:'
Get-ChildItem -LiteralPath $Root -Force | ForEach-Object {
  $kind = if ($_.PSIsContainer) { 'DIR ' } else { 'FILE' }
  Write-Report ("  {0}  {1}" -f $kind, $_.Name)
}
Write-Report ''

# ---------------------------------------------------------------------------
# 2) Group loose root files
# ---------------------------------------------------------------------------
Write-Report '=== 2) Group loose root files ==='
$GroupedRoot = Join-Path $Root '_grouped'
$moved = 0

$rootFiles = @(Get-ChildItem -LiteralPath $Root -File -Force -ErrorAction SilentlyContinue |
  Where-Object {
    $_.Name -ne $SelfName -and
    $KeepAtRoot -notcontains $_.Name
  })

foreach ($file in $rootFiles) {
  if (-not (Test-MayWritePath -FullPath $file.FullName)) { continue }
  $group = Get-GroupName -Extension $file.Extension
  $destDir = Join-Path $GroupedRoot $group
  $dest = Join-Path $destDir $file.Name
  if (-not (Test-MayWritePath -FullPath $dest)) { continue }
  Write-Report ("  MOVE  {0}  ->  _grouped\{1}\{2}" -f $file.Name, $group, $file.Name)
  if (-not $WhatIf) {
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    if (Test-Path -LiteralPath $dest) {
      $base = [IO.Path]::GetFileNameWithoutExtension($file.Name)
      $ext = $file.Extension
      $n = 1
      do {
        $dest = Join-Path $destDir ('{0}__{1}{2}' -f $base, $n, $ext)
        $n++
      } while (Test-Path -LiteralPath $dest)
    }
    Move-Item -LiteralPath $file.FullName -Destination $dest -Force
  }
  $moved++
}
Write-Report ("Moved: {0}" -f $moved)
Write-Report ''

# ---------------------------------------------------------------------------
# 3) Remove duplicates
# ---------------------------------------------------------------------------
Write-Report '=== 3) Remove duplicates ==='
$hashBuckets = @{}
$scanFiles = @(Get-ChildItem -LiteralPath $Root -File -Force -Recurse -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and
    $_.FullName -notmatch '\\node_modules\\' -and
    $_.FullName -notmatch '\\\.cursor\\' -and
    $_.Length -gt 0 -and
    $_.Name -ne $SelfName
  })

foreach ($file in $scanFiles) {
  try {
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
  } catch {
    continue
  }
  if (-not $hashBuckets.ContainsKey($hash)) {
    $hashBuckets[$hash] = New-Object System.Collections.Generic.List[string]
  }
  [void]$hashBuckets[$hash].Add($file.FullName)
}

$deletedDupes = 0
foreach ($hash in @($hashBuckets.Keys)) {
  $paths = @($hashBuckets[$hash])
  if ($paths.Count -lt 2) { continue }

  $ranked = @($paths | Sort-Object {
    $score = $_.Length
    if (Test-IsProtectedPath -FullPath $_) { $score -= 100000 }
    if ($_ -match '\\_grouped\\') { $score += 1000 }
    if ($_ -match '__from-') { $score += 500 }
    $score
  })

  $keep = $ranked[0]
  foreach ($dup in ($ranked | Select-Object -Skip 1)) {
    if (Test-IsProtectedPath -FullPath $dup) {
      Write-Report ("  KEEP(protected)  {0}" -f $dup)
      continue
    }
    if (-not (Test-MayWritePath -FullPath $dup)) { continue }
    Write-Report ("  DEL duplicate  {0}" -f $dup)
    Write-Report ("       kept      {0}" -f $keep)
    if (-not $WhatIf) {
      Remove-Item -LiteralPath $dup -Force -ErrorAction SilentlyContinue
    }
    $deletedDupes++
  }
}
Write-Report ("Duplicates removed: {0}" -f $deletedDupes)
Write-Report ''

# ---------------------------------------------------------------------------
# 4) Delete empty folders
# ---------------------------------------------------------------------------
Write-Report '=== 4) Delete empty folders ==='
$deletedEmpty = 0
for ($pass = 0; $pass -lt 20; $pass++) {
  $empties = @(Get-ChildItem -LiteralPath $Root -Directory -Force -Recurse -ErrorAction SilentlyContinue |
    Where-Object {
      -not (Test-IsProtectedPath -FullPath $_.FullName) -and
      @(Get-ChildItem -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue).Count -eq 0
    } |
    Sort-Object { $_.FullName.Length } -Descending)

  if ($empties.Count -eq 0) { break }

  foreach ($dir in $empties) {
    if (-not (Test-MayWritePath -FullPath $dir.FullName)) { continue }
    Write-Report ("  DEL empty  {0}" -f $dir.FullName)
    if (-not $WhatIf) {
      try {
        Remove-Item -LiteralPath $dir.FullName -Force -ErrorAction Stop
        $deletedEmpty++
      } catch {
        Write-Report ("  SKIP  {0}  ({1})" -f $dir.FullName, $_.Exception.Message)
      }
    } else {
      $deletedEmpty++
    }
  }
}
Write-Report ("Empty folders removed: {0}" -f $deletedEmpty)
Write-Report ''

Write-Report '=== Done ==='
Write-Report ("Summary: moved={0} dupes_deleted={1} empty_deleted={2}" -f $moved, $deletedDupes, $deletedEmpty)

$Lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8
Write-Host ''
Write-Host ("Full report: {0}" -f $ReportPath)
