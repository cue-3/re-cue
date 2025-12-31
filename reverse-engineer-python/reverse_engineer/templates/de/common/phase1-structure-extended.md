{% extends "base.md" %}

{% block title %}Phase 1: Projektstrukturanalyse - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Dieses Dokument enthält die Ergebnisse der Phase-1-Analyse: Entdeckung der grundlegenden
Struktur des Projekts einschließlich Endpunkte, Modelle, Ansichten, Dienste und Funktionen.
{% endblock %}

{% block overview_stats %}
- **API-Endpunkte**: {{ ENDPOINT_COUNT | default(0) }}
- **Datenmodelle**: {{ MODEL_COUNT | default(0) }}
- **UI-Ansichten**: {{ VIEW_COUNT | default(0) }}
- **Backend-Dienste**: {{ SERVICE_COUNT | default(0) }}
- **Funktionen**: {{ FEATURE_COUNT | default(0) }}
{% endblock %}

{% block main_content %}
## API-Endpunkte

{% if ENDPOINT_COUNT and ENDPOINT_COUNT > 0 %}
| Methode | Endpunkt | Controller |
|---------|----------|------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} |
{% endfor %}
{% else %}
*Keine API-Endpunkte erkannt.*
{% endif %}

---

## Datenmodelle

{% if MODEL_COUNT and MODEL_COUNT > 0 %}
| Modell | Felder | Speicherort |
|--------|--------|-------------|
{% for model in models %}
| {{ model.name }} | {{ model.fields | length }} | {{ model.location }} |
{% endfor %}
{% else %}
*Keine Datenmodelle erkannt.*
{% endif %}

---

## UI-Ansichten

{% if VIEW_COUNT and VIEW_COUNT > 0 %}
| Ansichtsname | Komponentendatei |
|--------------|------------------|
{% for view in views %}
| {{ view.name }} | {{ view.file }} |
{% endfor %}
{% else %}
*Keine UI-Ansichten erkannt.*
{% endif %}

---

## Backend-Dienste

{% if services %}
{% for service in services %}
### {{ service.name }}

- **Typ**: {{ service.type }}
- **Speicherort**: {{ service.location }}
{% if service.methods %}
- **Methoden**: {{ service.methods | length }}
{% endif %}

{% endfor %}
{% else %}
*Keine Backend-Dienste erkannt.*
{% endif %}

---

## Funktionen

{% if features %}
Die folgenden Funktionen wurden identifiziert:

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description | default('Keine Beschreibung') }}
{% endfor %}
{% else %}
*Keine Funktionen erkannt.*
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Akteure identifizieren, die mit dem System interagieren
- Benutzerrollen und Berechtigungen entdecken
- Externe Systeme und Integrationen abbilden
{% endblock %}