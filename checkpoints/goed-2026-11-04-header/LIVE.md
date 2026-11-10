# Live zetten — Gestalt Nu

De vernieuwde site staat in `site/`. Live domein blijft `https://www.gestaltnu.nl/`.

## Lokale preview (poort 8765) — vaste procedure

Gebruik altijd de scripts in `scripts/`. Niet handmatig een losse `HttpListener` of Store-`python` starten.

### Starten

```powershell
cd C:\Users\jeroe\gestaltnu-layout-voorbeeld
.\scripts\start-preview.ps1
```

Optioneel met browser:

```powershell
.\scripts\start-preview.ps1 -OpenBrowser
```

Andere map (bijv. doodles):

```powershell
.\scripts\start-preview.ps1 -Root ".\gestalt-nu-Grok\WELKE KANT WE OP GAAN"
```

- URL: http://127.0.0.1:8765/
- Standaard root: `site/`
- Engine: standaard **PowerShell** (leest grote bestanden zoals de hero-PNG volledig). Optioneel: `.\scripts\start-preview.ps1 -Engine python`
- Watchdog herstart de server automatisch als healthchecks falen
- Log: `%TEMP%\gestaltnu-preview-8765.log`
- Let op: `python -m http.server` knipte hier de hero-PNG (~8 MB) af → wit/kapot beeld in de browser

### Stoppen (voorkomt vastgelopen poort)

```powershell
.\scripts\stop-preview.ps1
```

Dit stopt server + watchdog en ruimt poort 8765 op. Doe dit vóór een nieuwe start als de preview “Can't connect” toont.

### Service worker tijdens bouwen

HTML/CSS/JS gaan **network-first** (`site/sw.js`, cache `gestalt-nu-schets-5`). Beelden blijven cache-first. Zie je tóch een oude pagina: hard refresh, of in DevTools → Application → Service Workers → Unregister.

## Voor live

1. Start de preview met `.\scripts\start-preview.ps1` (of open `site/index.html` lokaal).
2. Check telefoonbreedte: menu, WhatsApp-knop, hero.
3. Check links: groep, gesprekken, ademwerk, over, mindfulness.
4. Bevestig teksten met Jeroen (hardop).

## Deploy

1. Upload de inhoud van `site/` naar de hosting (statisch) **of** vervang WordPress-pagina’s één voor één met dezelfde URL-structuur.
2. Zorg dat deze bestanden op de root staan:
   - `llms.txt`
   - `robots.txt`
   - `sitemap.xml`
3. Redirects: houd `/gesprekken/`, `/bewustwordingsgroep/`, `/ademwerk/`, `/mindfulness/` intact. Nieuwe pagina: `/over/`.
4. Geen parallel merk (Therapie Rotterdam) op gestaltnu.nl.

## Na live

1. Google Search Console: sitemap indienen.
2. Rich results / schema even checken.
3. WhatsApp-test vanaf de telefoon.
