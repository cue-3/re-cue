{% extends "base.md" %}

{% block title %}Phase 2 : Découverte des Acteurs - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Ce document contient les résultats de l'analyse de la Phase 2 : identification des acteurs qui interagissent
avec le système, incluant les utilisateurs, les rôles, les systèmes externes et les services tiers.
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
{% include "_warning.md" %}

## Acteurs

{% if actors and actors | length > 0 %}
| Acteur | Type | Niveau d'Accès | Preuve |
|--------|------|----------------|---------|
{% for actor in actors %}
| {{ actor.name }} | {{ actor.type }} | {{ actor.access_level | default('N/A') }} | {{ actor.evidence | default('N/A') }} |
{% endfor %}

### Détails des Acteurs

{% for actor in actors %}
#### {{ actor.name }}

- **Type** : {{ actor.type }}
- **Niveau d'Accès** : {{ actor.access_level | default('Non spécifié') }}
{% if actor.permissions %}
- **Permissions** : {{ actor.permissions | join(', ') }}
{% endif %}
{% if actor.description %}
- **Description** : {{ actor.description }}
{% endif %}

{% endfor %}
{% else %}
*Aucun acteur n'a encore été identifié.*
{% endif %}

---

## Niveaux d'Accès

{% if access_levels %}
Les niveaux d'accès suivants ont été détectés :

{% for level in access_levels %}
- **{{ level.name }}** : {{ level.description | default('Aucune description') }}
  - Acteurs : {{ level.actor_count | default(0) }}
{% endfor %}
{% else %}
{{ ACCESS_LEVELS_SUMMARY | default('*Aucune information sur les niveaux d\'accès disponible*') }}
{% endif %}

---

## Annotations de Sécurité

{% if security_annotations %}
{% for annotation in security_annotations %}
- **{{ annotation.type }}** : Utilisée {{ annotation.count }} fois
{% if annotation.examples %}
  - Exemples : {{ annotation.examples | join(', ') }}
{% endif %}
{% endfor %}
{% else %}
{{ SECURITY_ANNOTATIONS_SUMMARY | default('*Aucune annotation de sécurité détectée*') }}
{% endif %}

---

## Relations entre Acteurs

{% if actor_relationships %}
{{ actor_relationships }}
{% else %}
{{ ACTOR_RELATIONSHIPS | default('*Aucune relation entre acteurs cartographiée*') }}
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Cartographier les frontières du système
- Identifier les sous-systèmes et les couches
- Documenter les interactions entre composants
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}