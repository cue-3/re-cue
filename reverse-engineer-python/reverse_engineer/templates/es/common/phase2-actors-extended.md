{% extends "base.md" %}

{% block title %}Fase 2: Descubrimiento de Actores - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Este documento contiene los resultados del análisis de la Fase 2: identificación de actores que interactúan
con el sistema, incluyendo usuarios, roles, sistemas externos y servicios de terceros.
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
{% include "_warning.md" %}

## Actores

{% if actors and actors | length > 0 %}
| Actor | Tipo | Nivel de Acceso | Evidencia |
|-------|------|-----------------|-----------|
{% for actor in actors %}
| {{ actor.name }} | {{ actor.type }} | {{ actor.access_level | default('N/A') }} | {{ actor.evidence | default('N/A') }} |
{% endfor %}

### Detalles de los Actores

{% for actor in actors %}
#### {{ actor.name }}

- **Tipo**: {{ actor.type }}
- **Nivel de Acceso**: {{ actor.access_level | default('No especificado') }}
{% if actor.permissions %}
- **Permisos**: {{ actor.permissions | join(', ') }}
{% endif %}
{% if actor.description %}
- **Descripción**: {{ actor.description }}
{% endif %}

{% endfor %}
{% else %}
*Aún no se han identificado actores.*
{% endif %}

---

## Niveles de Acceso

{% if access_levels %}
Se detectaron los siguientes niveles de acceso:

{% for level in access_levels %}
- **{{ level.name }}**: {{ level.description | default('Sin descripción') }}
  - Actores: {{ level.actor_count | default(0) }}
{% endfor %}
{% else %}
{{ ACCESS_LEVELS_SUMMARY | default('*No hay información disponible sobre niveles de acceso*') }}
{% endif %}

---

## Anotaciones de Seguridad

{% if security_annotations %}
{% for annotation in security_annotations %}
- **{{ annotation.type }}**: Utilizada {{ annotation.count }} vez/veces
{% if annotation.examples %}
  - Ejemplos: {{ annotation.examples | join(', ') }}
{% endif %}
{% endfor %}
{% else %}
{{ SECURITY_ANNOTATIONS_SUMMARY | default('*No se detectaron anotaciones de seguridad*') }}
{% endif %}

---

## Relaciones entre Actores

{% if actor_relationships %}
{{ actor_relationships }}
{% else %}
{{ ACTOR_RELATIONSHIPS | default('*No se han mapeado relaciones entre actores*') }}
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Mapear los límites del sistema
- Identificar subsistemas y capas
- Documentar las interacciones entre componentes
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}