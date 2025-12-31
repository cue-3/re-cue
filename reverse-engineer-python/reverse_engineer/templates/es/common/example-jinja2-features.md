# Ejemplo de Plantilla Mejorada con Jinja2

Esta plantilla demuestra las capacidades avanzadas habilitadas por la integración de Jinja2.

## Proyecto: {{ project_name | upper }}

**Generado**: {{ date }}
**Versión**: {{ version | default('1.0.0') }}

---

## Resumen de Características

{% if actor_count > 0 %}
### Actores ({{ actor_count }} en total)

Este proyecto ha identificado {{ actor_count }} actor{% if actor_count != 1 %}es{% endif %}:

{% for actor in actors %}
- **{{ actor.name }}** ({{ actor.type | replace('_', ' ') | title }})
  - Nivel de Acceso: {{ actor.access_level }}
  {% if actor.description %}
  - Descripción: {{ actor.description }}
  {% endif %}
{% endfor %}
{% else %}
*No se han identificado actores todavía.*
{% endif %}

---

{% if endpoints %}
## Endpoints de API ({{ endpoints | length }})

Los siguientes endpoints están disponibles:

| Método | Ruta | Autenticado | Descripción |
|--------|------|-------------|-------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {% if endpoint.authenticated %}🔒 Sí{% else %}No{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}

### Estadísticas de Endpoints

- Total de endpoints: {{ endpoints | length }}
- Endpoints autenticados: {{ endpoints | selectattr('authenticated') | list | length }}
- Endpoints públicos: {{ endpoints | rejectattr('authenticated') | list | length }}

### Métodos HTTP Utilizados

{% for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}**: {{ count }} endpoint{% if count != 1 %}s{% endif %}
{% endif %}
{% endfor %}

{% else %}
*No se descubrieron endpoints en este proyecto.*
{% endif %}

---

{% if models %}
## Modelos de Datos ({{ models | length }})

{% for model in models %}
### {{ loop.index }}. {{ model.name }}

- **Campos**: {{ model.fields }}
- **Ubicación**: `{{ model.location }}`
{% if model.relationships %}
- **Relaciones**: {{ model.relationships | join(', ') }}
{% endif %}

{% endfor %}
{% else %}
*No se encontraron modelos de datos.*
{% endif %}

---

## Métricas de Calidad

{% if test_coverage %}
### Cobertura de Pruebas

- General: {{ test_coverage.overall }}%
{% if test_coverage.overall >= 80 %}
- Estado: ✅ **Excelente** - Base de código bien probada
{% elif test_coverage.overall >= 60 %}
- Estado: ⚠️ **Bueno** - Considere agregar más pruebas
{% else %}
- Estado: ❌ **Necesita Mejora** - Baja cobertura de pruebas
{% endif %}
{% endif %}

{% if code_quality %}
### Calidad del Código

{% for metric, value in code_quality.items() %}
- {{ metric | replace('_', ' ') | title }}: {{ value }}
{% endfor %}
{% endif %}

---

## Recomendaciones

{% if recommendations %}
{% for category, items in recommendations.items() %}
### {{ category | title }}

{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{% endfor %}
{% else %}
*No hay recomendaciones en este momento.*
{% endif %}

---

## Resumen

Este análisis encontró:
{% if actor_count > 0 %}- {{ actor_count }} actor(es){% endif %}
{% if endpoints %}- {{ endpoints | length }} endpoint(s) de API{% endif %}
{% if models %}- {{ models | length }} modelo(s) de datos{% endif %}

{% if actor_count == 0 and (endpoints | length) == 0 and (models | length) == 0 %}
*El análisis del proyecto está incompleto. Por favor ejecute un análisis completo.*
{% else %}
*Análisis completo. Revise las secciones anteriores para información detallada.*
{% endif %}

---

*Generado por RE-cue con plantillas Jinja2*