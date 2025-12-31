# Erweitertes Vorlagenbeispiel mit Jinja2

Diese Vorlage demonstriert die erweiterten Funktionen, die durch die Jinja2-Integration ermöglicht werden.

## Projekt: {{ project_name | upper }}

**Generiert**: {{ date }}
**Version**: {{ version | default('1.0.0') }}

---

## Funktionsübersicht

{% if actor_count > 0 %}
### Akteure ({{ actor_count }} insgesamt)

Dieses Projekt hat {{ actor_count }} Akteur{% if actor_count != 1 %}e{% endif %} identifiziert:

{% for actor in actors %}
- **{{ actor.name }}** ({{ actor.type | replace('_', ' ') | title }})
  - Zugriffsebene: {{ actor.access_level }}
  {% if actor.description %}
  - Beschreibung: {{ actor.description }}
  {% endif %}
{% endfor %}
{% else %}
*Es wurden noch keine Akteure identifiziert.*
{% endif %}

---

{% if endpoints %}
## API-Endpunkte ({{ endpoints | length }})

Die folgenden Endpunkte sind verfügbar:

| Methode | Pfad | Authentifiziert | Beschreibung |
|---------|------|-----------------|--------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {% if endpoint.authenticated %}🔒 Ja{% else %}Nein{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}

### Endpunkt-Statistiken

- Endpunkte insgesamt: {{ endpoints | length }}
- Authentifizierte Endpunkte: {{ endpoints | selectattr('authenticated') | list | length }}
- Öffentliche Endpunkte: {{ endpoints | rejectattr('authenticated') | list | length }}

### Verwendete HTTP-Methoden

{% for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}**: {{ count }} Endpunkt{% if count != 1 %}e{% endif %}
{% endif %}
{% endfor %}

{% else %}
*In diesem Projekt wurden keine Endpunkte entdeckt.*
{% endif %}

---

{% if models %}
## Datenmodelle ({{ models | length }})

{% for model in models %}
### {{ loop.index }}. {{ model.name }}

- **Felder**: {{ model.fields }}
- **Speicherort**: `{{ model.location }}`
{% if model.relationships %}
- **Beziehungen**: {{ model.relationships | join(', ') }}
{% endif %}

{% endfor %}
{% else %}
*Keine Datenmodelle gefunden.*
{% endif %}

---

## Qualitätsmetriken

{% if test_coverage %}
### Testabdeckung

- Gesamt: {{ test_coverage.overall }}%
{% if test_coverage.overall >= 80 %}
- Status: ✅ **Ausgezeichnet** - Gut getestete Codebasis
{% elif test_coverage.overall >= 60 %}
- Status: ⚠️ **Gut** - Erwägen Sie, weitere Tests hinzuzufügen
{% else %}
- Status: ❌ **Verbesserungsbedarf** - Niedrige Testabdeckung
{% endif %}
{% endif %}

{% if code_quality %}
### Codequalität

{% for metric, value in code_quality.items() %}
- {{ metric | replace('_', ' ') | title }}: {{ value }}
{% endfor %}
{% endif %}

---

## Empfehlungen

{% if recommendations %}
{% for category, items in recommendations.items() %}
### {{ category | title }}

{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{% endfor %}
{% else %}
*Derzeit keine Empfehlungen.*
{% endif %}

---

## Zusammenfassung

Diese Analyse fand:
{% if actor_count > 0 %}- {{ actor_count }} Akteur(e){% endif %}
{% if endpoints %}- {{ endpoints | length }} API-Endpunkt(e){% endif %}
{% if models %}- {{ models | length }} Datenmodell(e){% endif %}

{% if actor_count == 0 and (endpoints | length) == 0 and (models | length) == 0 %}
*Die Projektanalyse ist unvollständig. Bitte führen Sie eine vollständige Analyse durch.*
{% else %}
*Analyse abgeschlossen. Überprüfen Sie die obigen Abschnitte für detaillierte Informationen.*
{% endif %}

---

*Generiert von RE-cue mit Jinja2-Vorlagen*