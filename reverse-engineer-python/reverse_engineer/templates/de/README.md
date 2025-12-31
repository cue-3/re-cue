# Deutsche Vorlagen

Dieses Verzeichnis enthält deutsche Vorlagen für die RE-cue-Dokumentationsgenerierung.

## Struktur

- `common/` - Gemeinsame Vorlagen für alle Frameworks
- `frameworks/` - Framework-spezifische Vorlagen
  - `java_spring/` - Java Spring Boot Vorlagen
  - `nodejs/` - Node.js (Express, NestJS) Vorlagen
  - `python/` - Python (Django, Flask, FastAPI) Vorlagen

## Vorlagendateien

### Gemeinsame Vorlagen

- `phase1-structure.md` - Phase 1: Projektstrukturanalyse
- `phase2-actors.md` - Phase 2: Akteurerkennung
- `phase3-boundaries.md` - Phase 3: Systemgrenzen
- `phase4-use-cases.md` - Phase 4: Anwendungsfallanalyse
- `4+1-architecture-template.md` - 4+1 Architektursicht-Vorlage
- `base.md` - Basisvorlage mit Vererbungsunterstützung
- `_footer.md` - Gemeinsame Fußzeilenkomponente
- `_stats_table.md` - Statistiktabellenkomponente
- `_warning.md` - Warnmeldungskomponente

### Framework-spezifische Vorlagen

Jedes Framework-Verzeichnis enthält spezialisierte Vorlagen, die gemeinsame Vorlagen
mit framework-spezifischer Formatierung und Terminologie überschreiben.

## Verwendung

Diese Vorlagen werden automatisch verwendet, wenn `--template-language de` dem
RE-cue-Befehlszeilenwerkzeug übergeben wird.
