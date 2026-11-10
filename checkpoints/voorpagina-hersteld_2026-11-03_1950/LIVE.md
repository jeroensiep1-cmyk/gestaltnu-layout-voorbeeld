# Live zetten — Gestalt Nu

De vernieuwde site staat in `site/`. Live domein blijft `https://www.gestaltnu.nl/`.

## Voor live

1. Open `site/index.html` lokaal in de browser (of een simpele static server).
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
