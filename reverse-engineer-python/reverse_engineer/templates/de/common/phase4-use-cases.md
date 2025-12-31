# Phase 4: Anwendungsfallanalyse
## {{PROJECT_NAME}}

**Generiert**: {{DATE}}
**Analysephase**: 4 von 4 - Anwendungsfall-Extraktion

---

## Überblick

Dieses Dokument enthält die Ergebnisse der Phase-4-Analyse: Extraktion von Anwendungsfällen aus den
identifizierten Akteuren, Systemgrenzen und Geschäftsprozessen.

Das {{PROJECT_NAME_DISPLAY}}-System umfasst {{ACTOR_COUNT}} identifizierte Akteure,
die über {{USE_CASE_COUNT}} Anwendungsfälle über
{{BOUNDARY_COUNT}} Systemgrenzen hinweg interagieren.

*Hinweis: Detaillierte Informationen zu Akteuren finden Sie in phase2-actors.md. Details zu Systemgrenzen finden Sie in phase3-boundaries.md.*

---

## Geschäftskontext

Die Analyse identifizierte die folgenden Geschäftsmuster und -einschränkungen:

| Kategorie | Anzahl | Details |
|-----------|--------|---------|
{{BUSINESS_CONTEXT}}

---

## Detaillierte Anwendungsfälle

{{USE_CASES_DETAILED}}

---

## Anwendungsfall-Beziehungen

{{USE_CASE_RELATIONSHIPS}}

---

## Akteur-Grenzen-Matrix

{{ACTOR_BOUNDARY_MATRIX}}

---

## Geschäftsregeln

{{BUSINESS_RULES}}

---

## Arbeitsabläufe und Prozesse

{{WORKFLOWS}}

---

## Erweiterungspunkte

{{EXTENSION_POINTS}}

---

## Validierungsregeln

{{VALIDATION_RULES}}

---

## Transaktionsgrenzen

{{TRANSACTION_BOUNDARIES}}

---

## Abschlusszusammenfassung

Alle 4 Phasen der Reverse-Engineering-Analyse sind nun abgeschlossen:

- ✅ **Phase 1**: Projektstrukturanalyse
- ✅ **Phase 2**: Akteur-Entdeckung
- ✅ **Phase 3**: Systemgrenzen-Mapping  
- ✅ **Phase 4**: Anwendungsfall-Extraktion

### Generierte Dokumentation

Die vollständige Analyse hat folgende Dokumente erstellt:
- `phase1-structure.md` - Projektstruktur und Komponenten
- `phase2-actors.md` - Akteur-Identifikation und Rollen
- `phase3-boundaries.md` - Systemgrenzen und Architektur
- `phase4-use-cases.md` - Anwendungsfälle und Geschäftsprozesse

### Nächste Schritte

1. **Überprüfen und Verfeinern**: Prüfen Sie alle generierten Dokumente auf Richtigkeit
2. **Konsolidieren**: Erstellen Sie bei Bedarf eine einheitliche Dokumentation
3. **Pflegen**: Aktualisieren Sie die Dokumentation bei Weiterentwicklung der Codebasis

---

*Generiert von RE-cue - Reverse Engineering Toolkit*