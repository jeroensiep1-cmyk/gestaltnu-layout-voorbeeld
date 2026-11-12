# Chat / Composer — instelling (11 nov 2026)

## Wat stuk was

- **Composer queue stond op `steer`** (`cursor.composer.queueMessageDefaultBehavior` en handmatig ook `steer`).
- Bij lopende agent **én** voice werden nieuwe berichten **gestuurd in de lopende turn** (steer), niet netjes in de wachtrij.
- Gevolg in logs: o.a. `Model sample preempted by pending steer`, `consumeStream aborted`, `RealtimeVoice … sent_after_wait (steer)` — antwoorden (vooral korte pad-regels) leken “weg” of kwamen niet in chat.

De agent-pipeline sloot turns wél af (`Request successful`); het probleem was **Composer-gedrag + weergave**, niet “niets verzonden”.

## Wat is aangepast (permanent)

Bestand: `%APPDATA%\Cursor\User\settings.json`

| Instelling | Was | Nu |
|------------|-----|-----|
| `cursor.composer.queueMessageDefaultBehavior` | `steer` | **`queue`** |
| `cursor.composer.queueManualSendBehavior2` | `steer` | **`interrupt`** |

**Herstart Cursor** of *Developer: Reload Window* zodat dit overal geldt.

## Extra (projectregel)

`.cursor/rules/chat-betrouwbaar-copy-paste.mdc` — agents zetten paden in codeblokken, geen path-only antwoorden, geen voice i.p.v. chat bij copy-paste.
