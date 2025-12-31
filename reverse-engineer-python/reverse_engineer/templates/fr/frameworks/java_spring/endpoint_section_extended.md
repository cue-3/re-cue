{% extends "base_framework_section.md" %}

{% block framework_name %}Java Spring Boot{% endblock %}
{% block section_title %}Section des Points de Terminaison{% endblock %}
{% block section_subtitle %}Points de Terminaison API{% endblock %}

{% block section_description %}les points de terminaison de l'API REST découverts dans l'application Spring Boot{% endblock %}

{% block summary_title %}Résumé des Points de Terminaison{% endblock %}

{% block summary_table_header %}
| Méthode | Chemin | Contrôleur | Authentification | Description |
|---------|--------|------------|------------------|-------------|
{% endblock %}

{% block summary_table_rows %}
{% if endpoints %}
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} | {% if endpoint.authenticated %}🔒 Oui{% else %}Non{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}
{% else %}
{{ ENDPOINT_ROWS | default('*Aucun point de terminaison trouvé*') }}
{% endif %}
{% endblock %}

{% block details_title %}Détails des Points de Terminaison{% endblock %}

{% block details_content %}
{% if endpoints %}
{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

- **Contrôleur** : {{ endpoint.controller }}
- **Méthode** : {{ endpoint.handler_method | default('N/A') }}
{% if endpoint.authenticated %}
- **Authentification** : Requise ({{ endpoint.auth_type | default('Spring Security') }})
{% endif %}
{% if endpoint.parameters %}
- **Paramètres** :
{% for param in endpoint.parameters %}
  - `{{ param.name }}` ({{ param.type }}){% if param.required %} - Requis{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
{{ ENDPOINT_DETAILS | default('*Aucune information détaillée sur les points de terminaison disponible*') }}
{% endif %}
{% endblock %}

{% block patterns_title %}Annotations Spring Utilisées{% endblock %}

{% block patterns_content %}
Les annotations Spring suivantes ont été détectées dans le code source :

{% block spring_annotations %}
- **@RestController** - Marque les classes comme contrôleurs REST
- **@RequestMapping** - Associe les requêtes HTTP aux méthodes de traitement
- **@GetMapping** - Gère les requêtes HTTP GET
- **@PostMapping** - Gère les requêtes HTTP POST
- **@PutMapping** - Gère les requêtes HTTP PUT
- **@DeleteMapping** - Gère les requêtes HTTP DELETE
- **@PatchMapping** - Gère les requêtes HTTP PATCH
{% endblock %}
{% endblock %}

{% block additional_sections %}
### Modèles de Mappage des Requêtes

{% if request_mappings %}
{% for mapping in request_mappings %}
- **{{ mapping.pattern }}** : Utilisé dans {{ mapping.count }} point(s) de terminaison
{% endfor %}
{% else %}
{{ REQUEST_MAPPING_DETAILS | default('*Aucun modèle de mappage de requête détecté*') }}
{% endif %}

---

### Types de Réponse

{% if response_types %}
{% for response in response_types %}
- **{{ response.type }}** : Retourné par {{ response.count }} point(s) de terminaison
{% endfor %}
{% else %}
{{ RESPONSE_TYPE_DETAILS | default('*Aucune information sur les types de réponse disponible*') }}
{% endif %}
{% endblock %}