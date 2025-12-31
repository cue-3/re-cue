# RE-cue Templates

Dieses Verzeichnis enthält Vorlagen für die Generierung von Reverse-Engineering-Dokumentation.

## Überblick über das Vorlagensystem

RE-cue verwendet **Jinja2**-Vorlagen mit Unterstützung für:
- ✅ **Template-Vererbung** (`extends`) - Gemeinsame Struktur wiederverwenden
- ✅ **Wiederverwendbare Komponenten** (`include`) - Gemeinsame Elemente teilen
- ✅ **Bedingtes Rendering** - Abschnitte basierend auf Daten ein-/ausblenden
- ✅ **Schleifen** - Über Sammlungen iterieren
- ✅ **Filter** - Daten für die Anzeige transformieren

Siehe [Template Inheritance Guide](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) für Details.

## Vorlagenkategorien

### Basisvorlagen (NEU in v1.4.0)

- **`base.md`** - Basisvorlage für alle Dokumentationen mit wiederverwendbaren Blöcken
- **`base_framework_section.md`** - Basis für Framework-spezifische Abschnitte

### Erweiterte Vorlagen (NEU in v1.4.0)

Vorlagen, die Vererbung für bessere Wartbarkeit nutzen:
- **`phase1-structure-extended.md`** - Erweiterte Phase 1 mit Vererbung
- **`phase2-actors-extended.md`** - Erweiterte Phase 2 mit Includes
- **`endpoint_section_extended.md`** - Framework-Abschnitt mit Vererbung

### Wiederverwendbare Komponenten (NEU in v1.4.0)

Mit `_` präfixiert zur einfachen Identifizierung:
- **`_stats_table.md`** - Statistiktabellen-Komponente
- **`_footer.md`** - Dokumentfußzeile mit Generierungsinformationen
- **`_warning.md`** - Warnbanner-Komponente

### Ursprüngliche Phasenvorlagen

Klassische Vorlagen (weiterhin unterstützt für Rückwärtskompatibilität):

### Phase 1: Projektstruktur (`phase1-structure.md`)
Dokumentiert die grundlegende Projektstruktur einschließlich:
- API-Endpunkte
- Datenmodelle
- UI-Ansichten
- Backend-Dienste
- Identifizierte Funktionen

### Phase 2: Akteur-Entdeckung (`phase2-actors.md`)
Dokumentiert identifizierte Akteure einschließlich:
- Interne Benutzer
- Endbenutzer
- Externe Systeme
- Zugriffsebenen und Sicherheit

### Phase 3: Systemgrenzen-Mapping (`phase3-boundaries.md`)
Dokumentiert die Systemarchitektur einschließlich:
- Systemgrenzen
- Subsysteme und Schichten
- Komponenten-Mapping
- Grenzen-Interaktionen

### Phase 4: Anwendungsfall-Extraktion (`phase4-use-cases.md`)
Dokumentiert Geschäftsprozesse einschließlich:
- Anwendungsfälle
- Akteur-Grenzen-Beziehungen
- Geschäftsregeln
- Workflows
- Validierungs- und Transaktionsgrenzen

## Vorlagenvariablen

Vorlagen verwenden das folgende Platzhalterformat: `{{VARIABLE_NAME}}`

### Allgemeine Variablen

- `{{PROJECT_NAME}}` - Projektname (kebab-case)
- `{{PROJECT_NAME_DISPLAY}}` - Projektname (Anzeigeformat)
- `{{DATE}}` - Generierungsdatum
- `{{PROJECT_PATH}}` - Absoluter Projektpfad

### Phasenspezifische Variablen

**Phase 1:**
- `{{ENDPOINT_COUNT}}`, `{{MODEL_COUNT}}`, `{{VIEW_COUNT}}`, `{{SERVICE_COUNT}}`, `{{FEATURE_COUNT}}`
- `{{ENDPOINTS_LIST}}`, `{{MODELS_LIST}}`, `{{VIEWS_LIST}}`, `{{SERVICES_LIST}}`, `{{FEATURES_LIST}}`

**Phase 2:**
- `{{ACTOR_COUNT}}`, `{{INTERNAL_USER_COUNT}}`, `{{END_USER_COUNT}}`, `{{EXTERNAL_SYSTEM_COUNT}}`
- `{{INTERNAL_USERS_LIST}}`, `{{END_USERS_LIST}}`, `{{EXTERNAL_SYSTEMS_LIST}}`
- `{{ACCESS_LEVELS_SUMMARY}}`, `{{SECURITY_ANNOTATIONS_SUMMARY}}`, `{{ACTOR_RELATIONSHIPS}}`

**Phase 3:**
- `{{BOUNDARY_COUNT}}`, `{{SUBSYSTEM_COUNT}}`, `{{LAYER_COUNT}}`, `{{COMPONENT_COUNT}}`
- `{{BOUNDARIES_LIST}}`, `{{SUBSYSTEM_ARCHITECTURE}}`, `{{LAYER_ORGANIZATION}}`
- `{{COMPONENT_MAPPING}}`, `{{BOUNDARY_INTERACTIONS}}`, `{{TECH_STACK_BY_BOUNDARY}}`

**Phase 4:**
- `{{USE_CASE_COUNT}}`, `{{ACTOR_COUNT}}`, `{{BOUNDARY_COUNT}}`
- `{{ACTORS_SUMMARY}}`, `{{BOUNDARIES_SUMMARY}}`, `{{USE_CASES_SUMMARY}}`
- `{{BUSINESS_CONTEXT}}`, `{{USE_CASES_DETAILED}}`, `{{USE_CASE_RELATIONSHIPS}}`
- `{{ACTOR_BOUNDARY_MATRIX}}`, `{{BUSINESS_RULES}}`, `{{WORKFLOWS}}`
- `{{EXTENSION_POINTS}}`, `{{VALIDATION_RULES}}`, `{{TRANSACTION_BOUNDARIES}}`

## Verwendung

Diese Vorlagen werden von den Phasendokument-Generatoren in `generators.py` verwendet. Um das Ausgabeformat von Phasendokumenten zu ändern, bearbeiten Sie die entsprechende Vorlagendatei.

### Beispiel: Anpassung der Phase 1-Ausgabe

1. Bearbeiten Sie `phase1-structure.md`
2. Ändern Sie die Struktur, fügen Sie Abschnitte hinzu oder ändern Sie die Formatierung
3. Behalten Sie Variablenplatzhalter (`{{VARIABLE}}`) bei
4. Der Generator verwendet automatisch die aktualisierte Vorlage

## Template-Vererbung (ENH-TMPL-003)

### Verwendung von Template-Vererbung

**Erstellen Sie eine benutzerdefinierte Vorlage, die die Basis erweitert:**

```jinja2
{% extends "base.md" %}

{% block title %}Meine Analyse - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
## Benutzerdefinierter Inhalt
{{ my_data }}
{% endblock %}
```

**Verwendung von Komponenten:**

```jinja2
{% include "_stats_table.md" %}
{% include "_footer.md" %}
```

### Verfügbare Basisvorlagen-Blöcke

**base.md:**
- `header` - Dokumentkopf
- `title` - Nur Titel
- `overview` - Übersichtsabschnitt
- `overview_content` - Übersichtstext
- `overview_stats` - Statistiken
- `main_content` - Hauptinhalt (überschreiben Sie diesen!)
- `next_steps` - Nächste Schritte
- `footer` - Fußzeile

### Migrationsleitfaden

Alte Vorlagen funktionieren weiterhin! Um neue Funktionen zu nutzen:

1. **Alte Vorlagen weiter verwenden** - Keine Änderung erforderlich
2. **Erweiterte Versionen erstellen** - Neue Vorlagen mit `-extended.md`-Suffix
3. **Schrittweise migrieren** - Generatoren aktualisieren, wenn bereit

## Ressourcen

- [Template Inheritance Guide](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) - Vollständiger Leitfaden
- [Template Examples](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-EXAMPLES.md) - Praktische Beispiele
- [Jinja2 Guide](../../../../../docs/JINJA2-TEMPLATE-GUIDE.md) - Jinja2-Funktionen

---

*Teil von RE-cue - Reverse Engineering Toolkit*