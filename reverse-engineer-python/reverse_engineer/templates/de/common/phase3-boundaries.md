# Phase 3: Systemgrenzen-Mapping
## {{PROJECT_NAME}}

**Generiert**: {{DATE}}
**Analysephase**: 3 von 4 - Systemgrenzen-Mapping

---

## Überblick

Dieses Dokument enthält die Ergebnisse der Phase-3-Analyse: Mapping von Systemgrenzen,
Subsystemen, Schichten und Komponenteninteraktionen.

- **Systemgrenzen**: {{BOUNDARY_COUNT}}
- **Subsysteme**: {{SUBSYSTEM_COUNT}}
- **Schichten**: {{LAYER_COUNT}}
- **Komponenten**: {{COMPONENT_COUNT}}

---

## Systemgrenzen

| Systemgrenze | Typ | Komponentenanzahl | Schlüsselkomponenten |
|--------------|-----|-------------------|----------------------|
{{BOUNDARIES_TABLE}}

---

## Subsystem-Architektur

| Subsystem | Komponenten | Schnittstellen | Komponentenliste |
|-----------|-------------|----------------|------------------|
{{SUBSYSTEM_ARCHITECTURE}}

---

## Schichtenorganisation

{{LAYER_ORGANIZATION}}

---

## Komponenten-Mapping

{{COMPONENT_MAPPING}}

---

## Grenzinteraktionen

{{BOUNDARY_INTERACTIONS}}

---

## Technologie-Stack nach Grenzen

{{TECH_STACK_BY_BOUNDARY}}

---

## Nächste Schritte

Nach Überprüfung des Grenzen-Mappings:

1. **Weiter zu Phase 4**: Anwendungsfall-Extraktion
   - Anwendungsfälle aus Akteur-Grenze-Interaktionen identifizieren
   - Geschäftsprozesse extrahieren
   - Szenarien und Arbeitsabläufe dokumentieren

2. **Befehl zum Fortfahren**:
   ```bash
   python3 -m reverse_engineer --phase 4 --path {{PROJECT_PATH}}
   ```

---

*Generiert von RE-cue - Reverse Engineering Toolkit*