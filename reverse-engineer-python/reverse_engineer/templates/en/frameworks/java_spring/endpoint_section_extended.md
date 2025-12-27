{% extends "base_framework_section.md" %}

{% block framework_name %}Java Spring Boot{% endblock %}
{% block section_title %}Endpoint Section{% endblock %}
{% block section_subtitle %}API Endpoints{% endblock %}

{% block section_description %}the REST API endpoints discovered in the Spring Boot application{% endblock %}

{% block summary_title %}Endpoint Summary{% endblock %}

{% block summary_table_header %}
| Method | Path | Controller | Authentication | Description |
|--------|------|------------|----------------|-------------|
{% endblock %}

{% block summary_table_rows %}
{% if endpoints %}
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} | {% if endpoint.authenticated %}🔒 Yes{% else %}No{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}
{% else %}
{{ ENDPOINT_ROWS | default('*No endpoints found*') }}
{% endif %}
{% endblock %}

{% block details_title %}Endpoint Details{% endblock %}

{% block details_content %}
{% if endpoints %}
{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

- **Controller**: {{ endpoint.controller }}
- **Method**: {{ endpoint.handler_method | default('N/A') }}
{% if endpoint.authenticated %}
- **Authentication**: Required ({{ endpoint.auth_type | default('Spring Security') }})
{% endif %}
{% if endpoint.parameters %}
- **Parameters**:
{% for param in endpoint.parameters %}
  - `{{ param.name }}` ({{ param.type }}){% if param.required %} - Required{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
{{ ENDPOINT_DETAILS | default('*No detailed endpoint information available*') }}
{% endif %}
{% endblock %}

{% block patterns_title %}Spring Annotations Used{% endblock %}

{% block patterns_content %}
The following Spring annotations were detected in the codebase:

{% block spring_annotations %}
- **@RestController** - Marks classes as REST controllers
- **@RequestMapping** - Maps HTTP requests to handler methods
- **@GetMapping** - Handles HTTP GET requests
- **@PostMapping** - Handles HTTP POST requests
- **@PutMapping** - Handles HTTP PUT requests
- **@DeleteMapping** - Handles HTTP DELETE requests
- **@PatchMapping** - Handles HTTP PATCH requests
{% endblock %}
{% endblock %}

{% block additional_sections %}
### Request Mapping Patterns

{% if request_mappings %}
{% for mapping in request_mappings %}
- **{{ mapping.pattern }}**: Used in {{ mapping.count }} endpoint(s)
{% endfor %}
{% else %}
{{ REQUEST_MAPPING_DETAILS | default('*No request mapping patterns detected*') }}
{% endif %}

---

### Response Types

{% if response_types %}
{% for response in response_types %}
- **{{ response.type }}**: Returned by {{ response.count }} endpoint(s)
{% endfor %}
{% else %}
{{ RESPONSE_TYPE_DETAILS | default('*No response type information available*') }}
{% endif %}
{% endblock %}
