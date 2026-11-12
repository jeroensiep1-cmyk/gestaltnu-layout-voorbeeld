# AGENTS.md — Gestalt Nu

Afsprakenlijst voor dit project. Lees dit bestand **helemaal** vóór je handelt.

## Hoe deze afspraken zich verhouden

| Bron | Rol |
|------|-----|
| **Dit bestand (`AGENTS.md`)** | Site- en werkafspraken voor de agent in dit workspace |
| **`.cursor/rules/`** | Altijd-aan regels die Cursor automatisch meeneemt; details die hieronder al staan worden daar **niet** herhaald — alleen unieke of samenvattende verwijzingen |
| **`Gestalt Nu Cursor` (bureaublad)** | Centrale map voor opslag/output — zie §0 |

User-rules in Cursor Settings (dubbelcheck, bewustwordingsgroep, kortingscodes) blijven gelden naast dit bestand.

---

## 0. Centrale map — Gestalt Nu Cursor

- Pad: `C:\Users\jeroe\OneDrive\Bureaublad\Gestalt Nu Cursor`
- Deze map staat **bewust** op het bureaublad. Het is de centrale plek waar werk naartoe gaat — **geen** rommelmap, **niet** verwijderen of verplaatsen.
- Submappen (bestemmingen): `afbeeldingen`, `marketing`, `nieuwe website`
- Afbeeldingen (png/jpg/jpeg/webp/gif/svg, ook raw/clean/done/verify) → uitsluitend `…\Gestalt Nu Cursor\afbeeldingen` (niet naar `gestaltnu-layout-voorbeeld\afbeeldingen`)
- Geen afbeelding → juiste submap onder `Gestalt Nu Cursor` (niet los op het bureaublad)
- Workspace voor site-code blijft: `C:\Users\jeroe\gestaltnu-layout-voorbeeld` (canonieke bron `site/`)
- Volledige opslag-/doorwerk-lijst: `.cursor/rules/altijd-doorgaan.mdc`

## Context

| Wat | Waarde |
|-----|--------|
| Soort project | Statische HTML-site |
| Canonieke bron | `site/` |
| Live | `https://www.gestaltnu.nl/` |
| Lokale preview | `http://127.0.0.1:8765/` |
| Centrale opslag | `C:\Users\jeroe\OneDrive\Bureaublad\Gestalt Nu Cursor` |

---

## 1. Wat mag je wijzigen

- Bewerk **alleen** bestanden onder `site/`, tenzij Jeroen iets anders vraagt.
- Raak **niet** aan zonder expliciete opdracht:
  - live URLs / hosting
  - `checkpoints/`
  - doodle- en experimentmappen, o.a. `blokken/`, `direct/`, `vorm/`, `wit/`, `zacht/`, `inkt/`, `lijn/`, `papier/`, `strip/`, `tekeningen/`, `gestalt-nu-Grok/`, `sieposium-site/`

## 2. Dubbelcheck — geen aannames

- Dubbelcheck altijd vóór je iets presenteert of aanneemt.
- Geen aannames of oordelen: eerst verifiëren (bestand, pad, URL, preview, wat er echt staat).
- Bij twijfel: vragen, niet raden.
- Resultaat pas “klaar” noemen als je het zelf hebt gecontroleerd.
- Leer van je eigen fouten en verbeter jezelf.
- Context: Jeroen heeft te lang vooral Cursor-fouten moeten oplossen; aannames zijn de kernfout die hier stopt.

## 3. Bekijken ≠ toepassen

- Een opdracht tot **bekijken**, **openen** of **vergelijken** is **geen** toestemming om te wijzigen.
- Pas iets toe pas na een duidelijke ja, bijvoorbeeld: “doe maar”, “zet dit erop”, “vervang X door Y”.
- Doe **één** gevraagde wijziging per keer, tenzij Jeroen een lijst of “alles tegelijk” vraagt.

## 4. Preview vóór afronden

- Gebruik de scripts in `scripts/` — start **geen** handmatige losse preview-server.
- Starten: `.\scripts\start-preview.ps1`
- Stoppen: `.\scripts\stop-preview.ps1`
- Controleer daarna kort: juist pad, juist beeld, geen ongewenste sectie — pas daarna “klaar” melden.

## 5. Fouten meteen herstellen

- Zie je tijdens het werk een fout of vergissing: **fix die in dezelfde beurt**.
- Noteer fouten niet alleen “voor later”; herstel ze nu.
- Fout = kort erkennen + direct handelen; geen excuses.

## 6. Spelling en labels

- Bij **goedgekeurd** werk aan de site: zet duidelijke spelfouten in zichtbare tekst meteen recht.
- Verandert een term in een zin of kop: pas het bijbehorende label in **hetzelfde blok** mee aan. Laat geen oud label achter.

## 7. Voice call — chattekst kan onzichtbaar zijn

Known issue (gedocumenteerd 12 nov 2026; ook gezien 11 nov 2026). Details: `nieuwe website/known-issue-voice-chat-niet-zichtbaar.md`.

- Tijdens een voice call komen agent-teksten **vaak niet** als normale chatbubbels bij Jeroen in beeld (voice/transcript i.p.v. chat; soms `SendToCall` → “No call is listening” terwijl er wél een call open lijkt).
- Jeroen typt moeilijk; hij heeft **zichtbare** tekst nodig om te volgen en te kopiëren.
- **Doe dit:** belangrijke tekst **langzaam hardop voorlezen**, en/of naar een bestand onder `Gestalt Nu Cursor` schrijven en **openen**. Niet beweren dat chattekst “klaar staat” zonder dat hij het ziet of bevestigt.
