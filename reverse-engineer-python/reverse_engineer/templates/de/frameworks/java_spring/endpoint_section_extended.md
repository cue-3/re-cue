{% extends "base_framework_section.md" %}

{% block framework_name %}Java Spring Boot{% endblock %}
{% block section_title %}Endpunkt-Abschnitt{% endblock %}
{% block section_subtitle %}API-Endpunkte{% endblock %}

{% block section_description %}die REST-API-Endpunkte, die in der Spring Boot-Anwendung entdeckt wurden{% endblock %}

{% block summary_title %}Endpunkt-Zusammenfassung{% endblock %}

{% block summary_table_header %}
| Methode | Pfad | Controller | Authentifizierung | Beschreibung |
|---------|------|------------|-------------------|--------------|
{% endblock %}

{% block summary_table_rows %}
{% if endpoints %}
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} | {% if endpoint.authenticated %}🔒 Ja{% else %}Nein{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}
{% else %}
{{ ENDPOINT_ROWS | default('*Keine Endpunkte gefunden*') }}
{% endif %}
{% endblock %}

{% block details_title %}Endpunkt-Details{% endblock %}

{% block details_content %}
{% if endpoints %}
{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

- **Controller**: {{ endpoint.controller }}
- **Methode**: {{ endpoint.handler_method | default('N/A') }}
{% if endpoint.authenticated %}
- **Authentifizierung**: Erforderlich ({{ endpoint.auth_type | default('Spring Security') }})
{% endif %}
{% if endpoint.parameters %}
- **Parameter**:
{% for param in endpoint.parameters %}
  - `{{ param.name }}` ({{ param.type }}){% if param.required %} - Erforderlich{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
{{ ENDPOINT_DETAILS | default('*Keine detaillierten Endpunkt-Informationen verfügbar*') }}
{% endif %}
{% endblock %}

{% block patterns_title %}Verwendete Spring-Annotationen{% endblock %}

{% block patterns_content %}
Die folgenden Spring-Annotationen wurden im Codebestand erkannt:

{% block spring_annotations %}
- **@RestController** - Kennzeichnet Klassen als REST-Controller
- **@RequestMapping** - Ordnet HTTP-Anfragen Handler-Methoden zu
- **@GetMapping** - Verarbeitet HTTP GET-Anfragen
- **@PostMapping** - Verarbeitet HTTP POST-Anfragen
- **@PutMapping** - Verarbeitet HTTP PUT-Anfragen
- **@DeleteMapping** - Verarbeitet HTTP DELETE-Anfragen
- **@PatchMapping** - Verarbeitet HTTP PATCH-Anfragen
{% endblock %}
{% endblock %}

{% block additional_sections %}
### Request-Mapping-Muster

{% if request_mappings %}
{% for mapping in request_mappings %}
- **{{ mapping.pattern }}**: Verwendet in {{ mapping.count }} Endpunkt(en)
{% endfor %}
{% else %}
{{ REQUEST_MAPPING_DETAILS | default('*Keine Request-Mapping-Muster erkannt*') }}
{% endif %}

---

### Antworttypen

{% if response_types %}
{% for response in response_types %}
- **{{ response.type }}**: Zurückgegeben von {{ response.count }} Endpunkt(en)
{% endfor %}
{% else %}
{{ RESPONSE_TYPE_DETAILS | default('*Keine Informationen zu Antworttypen verfügbar*') }}
{% endif %}
{% endblock %}