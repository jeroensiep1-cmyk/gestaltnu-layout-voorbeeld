# Known issue — voice call: chattekst niet zichtbaar

**Status:** bekend, terugkerend  
**Eerste melding in dit project:** 11 november 2026 (gisteren t.o.v. documentatie)  
**Gedocumenteerd:** 12 november 2026  
**Ernst:** hoog voor Jeroen — typen is moeilijk; hij steunt op zichtbare chattekst om te kopiëren en te volgen.

---

## Symptomen

- Jeroen zit in een **voice call**.
- De agent zegt dat tekst “in de chat is geplaatst”.
- Op Jeroens scherm verschijnt die tekst **niet** als gewoon chatbericht.
- Is **meerdere keren** gebeurd, ook op 11 november 2026.

---

## Wat onderzoek vond (12 nov 2026)

Waarschijnlijk **voice/chat-kanaalscheiding**, geen gewone “vergeten te schrijven”:

1. Voice-prompts en antwoorden komen vaak **niet** als normale chatbubbels; ze kunnen in een **voice transcript** zitten (o.a. via “View transcript” op de voice-card). Forum/docs: sinds ~Cursor 3.27 is dit deels bewust gedrag.
2. **Sync-mismatch:** systeem zegt dat er een voice call open is, maar `SendToCall` antwoordt herhaaldelijk: `No call is listening.` De agent denkt dat er een kanaal is; Jeroen ziet/hoort niets betrouwbaars.
3. Antwoorden via een **subagent/parent** kunnen in een andere timeline landen dan het paneel dat Jeroen aankijkt.

---

## Werkafspraak voor agents

Tijdens een voice call (of als Jeroen zegt dat chattekst ontbreekt):

1. **Niet** aannemen dat een chatbericht zichtbaar is.
2. Belangrijke kopieertekst **hardop langzaam voorlezen**.
3. En/of naar een **bestand schrijven en openen** onder `Gestalt Nu Cursor` (juiste submap), zodat Jeroen het op scherm ziet.
4. Pas “zichtbaar” zeggen als Jeroen het bevestigt, of als een geopend bestand aantoonbaar de tekst toont.

Zie ook: `AGENTS.md` §7 · `START-OVERZICHT.md` §12
