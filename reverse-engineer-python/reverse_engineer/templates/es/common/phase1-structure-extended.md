{% extends "base.md" %}

{% block title %}Fase 1: Análisis de Estructura del Proyecto - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Este documento contiene los resultados del análisis de la Fase 1: descubrimiento de la estructura
básica del proyecto incluyendo endpoints, modelos, vistas, servicios y características.
{% endblock %}

{% block overview_stats %}
- **Endpoints de API**: {{ ENDPOINT_COUNT | default(0) }}
- **Modelos de Datos**: {{ MODEL_COUNT | default(0) }}
- **Vistas de UI**: {{ VIEW_COUNT | default(0) }}
- **Servicios Backend**: {{ SERVICE_COUNT | default(0) }}
- **Características**: {{ FEATURE_COUNT | default(0) }}
{% endblock %}

{% block main_content %}
## Endpoints de API

{% if ENDPOINT_COUNT and ENDPOINT_COUNT > 0 %}
| Método | Endpoint | Controlador |
|--------|----------|-------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} |
{% endfor %}
{% else %}
*No se detectaron endpoints de API.*
{% endif %}

---

## Modelos de Datos

{% if MODEL_COUNT and MODEL_COUNT > 0 %}
| Modelo | Campos | Ubicación |
|--------|--------|-----------|
{% for model in models %}
| {{ model.name }} | {{ model.fields | length }} | {{ model.location }} |
{% endfor %}
{% else %}
*No se detectaron modelos de datos.*
{% endif %}

---

## Vistas de UI

{% if VIEW_COUNT and VIEW_COUNT > 0 %}
| Nombre de Vista | Archivo de Componente |
|-----------------|----------------------|
{% for view in views %}
| {{ view.name }} | {{ view.file }} |
{% endfor %}
{% else %}
*No se detectaron vistas de UI.*
{% endif %}

---

## Servicios Backend

{% if services %}
{% for service in services %}
### {{ service.name }}

- **Tipo**: {{ service.type }}
- **Ubicación**: {{ service.location }}
{% if service.methods %}
- **Métodos**: {{ service.methods | length }}
{% endif %}

{% endfor %}
{% else %}
*No se detectaron servicios backend.*
{% endif %}

---

## Características

{% if features %}
Se identificaron las siguientes características:

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description | default('Sin descripción') }}
{% endfor %}
{% else %}
*No se detectaron características.*
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Identificar actores que interactúan con el sistema
- Descubrir roles de usuario y permisos
- Mapear sistemas externos e integraciones
{% endblock %}