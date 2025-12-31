{% extends "base.md" %}

{% block title %}Phase 2: Akteur-Erkennung - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Dieses Dokument enthält die Ergebnisse der Phase-2-Analyse: Identifizierung von Akteuren, die mit
dem System interagieren, einschließlich Benutzer, Rollen, externe Systeme und Drittanbieterdienste.
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
{% include "_warning.md" %}

## Akteure

{% if actors and actors | length > 0 %}
| Akteur | Typ | Zugriffsebene | Nachweis |
|--------|-----|---------------|----------|
{% for actor in actors %}
| {{ actor.name }} | {{ actor.type }} | {{ actor.access_level | default('N/A') }} | {{ actor.evidence | default('N/A') }} |
{% endfor %}

### Akteur-Details

{% for actor in actors %}
#### {{ actor.name }}

- **Typ**: {{ actor.type }}
- **Zugriffsebene**: {{ actor.access_level | default('Nicht angegeben') }}
{% if actor.permissions %}
- **Berechtigungen**: {{ actor.permissions | join(', ') }}
{% endif %}
{% if actor.description %}
- **Beschreibung**: {{ actor.description }}
{% endif %}

{% endfor %}
{% else %}
*Es wurden noch keine Akteure identifiziert.*
{% endif %}

---

## Zugriffsebenen

{% if access_levels %}
Die folgenden Zugriffsebenen wurden erkannt:

{% for level in access_levels %}
- **{{ level.name }}**: {{ level.description | default('Keine Beschreibung') }}
  - Akteure: {{ level.actor_count | default(0) }}
{% endfor %}
{% else %}
{{ ACCESS_LEVELS_SUMMARY | default('*Keine Informationen zu Zugriffsebenen verfügbar*') }}
{% endif %}

---

## Sicherheitsannotationen

{% if security_annotations %}
{% for annotation in security_annotations %}
- **{{ annotation.type }}**: {{ annotation.count }} Mal verwendet
{% if annotation.examples %}
  - Beispiele: {{ annotation.examples | join(', ') }}
{% endif %}
{% endfor %}
{% else %}
{{ SECURITY_ANNOTATIONS_SUMMARY | default('*Keine Sicherheitsannotationen erkannt*') }}
{% endif %}

---

## Akteur-Beziehungen

{% if actor_relationships %}
{{ actor_relationships }}
{% else %}
{{ ACTOR_RELATIONSHIPS | default('*Keine Akteur-Beziehungen zugeordnet*') }}
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Systemgrenzen abbilden
- Subsysteme und Schichten identifizieren
- Komponenteninteraktionen dokumentieren
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}