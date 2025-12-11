{% extends "base.md" %}

{% block title %}Phase 2: Actor Discovery - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
This document contains the results of Phase 2 analysis: identifying actors who interact
with the system, including users, roles, external systems, and third-party services.
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
{% include "_warning.md" %}

## Actors

{% if actors and actors | length > 0 %}
| Actor | Type | Access Level | Evidence |
|-------|------|--------------|----------|
{% for actor in actors %}
| {{ actor.name }} | {{ actor.type }} | {{ actor.access_level | default('N/A') }} | {{ actor.evidence | default('N/A') }} |
{% endfor %}

### Actor Details

{% for actor in actors %}
#### {{ actor.name }}

- **Type**: {{ actor.type }}
- **Access Level**: {{ actor.access_level | default('Not specified') }}
{% if actor.permissions %}
- **Permissions**: {{ actor.permissions | join(', ') }}
{% endif %}
{% if actor.description %}
- **Description**: {{ actor.description }}
{% endif %}

{% endfor %}
{% else %}
*No actors have been identified yet.*
{% endif %}

---

## Access Levels

{% if access_levels %}
The following access levels were detected:

{% for level in access_levels %}
- **{{ level.name }}**: {{ level.description | default('No description') }}
  - Actors: {{ level.actor_count | default(0) }}
{% endfor %}
{% else %}
{{ ACCESS_LEVELS_SUMMARY | default('*No access level information available*') }}
{% endif %}

---

## Security Annotations

{% if security_annotations %}
{% for annotation in security_annotations %}
- **{{ annotation.type }}**: Used {{ annotation.count }} time(s)
{% if annotation.examples %}
  - Examples: {{ annotation.examples | join(', ') }}
{% endif %}
{% endfor %}
{% else %}
{{ SECURITY_ANNOTATIONS_SUMMARY | default('*No security annotations detected*') }}
{% endif %}

---

## Actor Relationships

{% if actor_relationships %}
{{ actor_relationships }}
{% else %}
{{ ACTOR_RELATIONSHIPS | default('*No actor relationships mapped*') }}
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Map system boundaries
- Identify subsystems and layers
- Document component interactions
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}
