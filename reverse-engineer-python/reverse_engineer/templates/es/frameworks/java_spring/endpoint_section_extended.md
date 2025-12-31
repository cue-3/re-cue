{% extends "base_framework_section.md" %}

{% block framework_name %}Java Spring Boot{% endblock %}
{% block section_title %}Sección de Endpoints{% endblock %}
{% block section_subtitle %}Endpoints de API{% endblock %}

{% block section_description %}los endpoints de la API REST descubiertos en la aplicación Spring Boot{% endblock %}

{% block summary_title %}Resumen de Endpoints{% endblock %}

{% block summary_table_header %}
| Método | Ruta | Controlador | Autenticación | Descripción |
|--------|------|-------------|---------------|-------------|
{% endblock %}

{% block summary_table_rows %}
{% if endpoints %}
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} | {% if endpoint.authenticated %}🔒 Sí{% else %}No{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}
{% else %}
{{ ENDPOINT_ROWS | default('*No se encontraron endpoints*') }}
{% endif %}
{% endblock %}

{% block details_title %}Detalles de Endpoints{% endblock %}

{% block details_content %}
{% if endpoints %}
{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

- **Controlador**: {{ endpoint.controller }}
- **Método**: {{ endpoint.handler_method | default('N/A') }}
{% if endpoint.authenticated %}
- **Autenticación**: Requerida ({{ endpoint.auth_type | default('Spring Security') }})
{% endif %}
{% if endpoint.parameters %}
- **Parámetros**:
{% for param in endpoint.parameters %}
  - `{{ param.name }}` ({{ param.type }}){% if param.required %} - Requerido{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
{{ ENDPOINT_DETAILS | default('*No hay información detallada de endpoints disponible*') }}
{% endif %}
{% endblock %}

{% block patterns_title %}Anotaciones de Spring Utilizadas{% endblock %}

{% block patterns_content %}
Las siguientes anotaciones de Spring fueron detectadas en el código:

{% block spring_annotations %}
- **@RestController** - Marca las clases como controladores REST
- **@RequestMapping** - Mapea solicitudes HTTP a métodos manejadores
- **@GetMapping** - Maneja solicitudes HTTP GET
- **@PostMapping** - Maneja solicitudes HTTP POST
- **@PutMapping** - Maneja solicitudes HTTP PUT
- **@DeleteMapping** - Maneja solicitudes HTTP DELETE
- **@PatchMapping** - Maneja solicitudes HTTP PATCH
{% endblock %}
{% endblock %}

{% block additional_sections %}
### Patrones de Mapeo de Solicitudes

{% if request_mappings %}
{% for mapping in request_mappings %}
- **{{ mapping.pattern }}**: Utilizado en {{ mapping.count }} endpoint(s)
{% endfor %}
{% else %}
{{ REQUEST_MAPPING_DETAILS | default('*No se detectaron patrones de mapeo de solicitudes*') }}
{% endif %}

---

### Tipos de Respuesta

{% if response_types %}
{% for response in response_types %}
- **{{ response.type }}**: Devuelto por {{ response.count }} endpoint(s)
{% endfor %}
{% else %}
{{ RESPONSE_TYPE_DETAILS | default('*No hay información disponible sobre tipos de respuesta*') }}
{% endif %}
{% endblock %}