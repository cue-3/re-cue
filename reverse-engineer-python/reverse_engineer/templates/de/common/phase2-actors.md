# Phase 2: Akteur-Erkennung
## {{PROJECT_NAME}}

**Generiert**: {{DATE}}
**Analysephase**: 2 von 4 - Akteur-Erkennung

---

## Überblick

Dieses Dokument enthält die Ergebnisse der Phase-2-Analyse: Identifizierung von Akteuren, die mit
dem System interagieren, einschließlich Benutzer, Rollen, externe Systeme und Drittanbieterdienste.

- **Akteure gesamt**: {{ACTOR_COUNT}}
- **Interne Benutzer**: {{INTERNAL_USER_COUNT}}
- **Endbenutzer**: {{END_USER_COUNT}}
- **Externe Systeme**: {{EXTERNAL_SYSTEM_COUNT}}

---

## Akteure

| Akteur | Typ | Zugriffsebene | Nachweis |
|--------|-----|---------------|----------|
| {{ACTOR}} | {{ACTOR_TYPE}} | {{ACTOR_ACCESS_LEVEL}} | {{ACTOR_EVIDENCE}} |

---

## Zugriffsebenen

{{ACCESS_LEVELS_SUMMARY}}

---

## Sicherheitsannotationen

{{SECURITY_ANNOTATIONS_SUMMARY}}

---

## Akteur-Beziehungen

{{ACTOR_RELATIONSHIPS}}

---

## Nächste Schritte

Nach Überprüfung der Akteur-Analyse:

1. **Weiter zu Phase 3**: Systemgrenzen-Zuordnung
   - Akteure den Systemgrenzen zuordnen
   - Subsysteme und Schichten identifizieren
   - Komponenteninteraktionen definieren

2. **Befehl zum Fortfahren**:
   ```bash
   python3 -m reverse_engineer --phase 3 --path {{PROJECT_PATH}}
   ```

---

*Generiert von RE-cue - Reverse Engineering Toolkit*