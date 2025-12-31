# Phase 1: Projektstrukturanalyse
## {{PROJECT_NAME}}

**Erstellt**: {{DATE}}
**Analysephase**: 1 von 4 - Projektstruktur

---

## Überblick

Dieses Dokument enthält die Ergebnisse der Phase-1-Analyse: Ermittlung der grundlegenden
Struktur des Projekts einschließlich Endpunkte, Modelle, Ansichten, Dienste und Funktionen.

- **API-Endpunkte**: {{ENDPOINT_COUNT}}
- **Datenmodelle**: {{MODEL_COUNT}}
- **UI-Ansichten**: {{VIEW_COUNT}}
- **Backend-Dienste**: {{SERVICE_COUNT}}
- **Funktionen**: {{FEATURE_COUNT}}

---

## API-Endpunkte

| Methode | Endpunkt | Controller |
|---------|----------|------------|
| {{HTTP_METHOD}} | {{HTTP_ENDPOINT}} | {{API_CONTROLLER}} |

---

## Datenmodelle

| Modell | Felder | Speicherort |
|--------|--------|-------------|
| {{MODEL}} | {{FIELDS}} | {{DATA_MODEL_LOCATION}} |

---

## UI-Ansichten

| Ansichtsname | Komponentendatei |
|--------------|------------------|
| {{UI_VIEW_NAME}} | {{UI_COMPONENT_FILE}} |

---

## Backend-Dienste

{{SERVICES_LIST}}

---

## Funktionen

| # | Name | Beschreibung |
|---|------|--------------|
{{FEATURES_TABLE}}

---

## Nächste Schritte

Nach Überprüfung dieser Strukturanalyse:

1. **Weiter zu Phase 2**: Akteur-Ermittlung
   - Benutzer, Rollen und externe Systeme identifizieren
   - Sicherheitsannotationen den Akteuren zuordnen
   - Zugriffsebenen bestimmen

2. **Befehl zum Fortfahren**:
   ```bash
   python3 -m reverse_engineer --phase 2 --path {{PROJECT_PATH}}
   ```

---

*Erstellt von RE-cue - Reverse Engineering Toolkit*