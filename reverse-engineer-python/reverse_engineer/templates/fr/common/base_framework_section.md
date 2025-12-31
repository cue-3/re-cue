{# Base Template for Framework-Specific Sections #}
{# This template provides a consistent structure for framework sections #}

{% block section_header %}
# {% block framework_name %}Framework{% endblock %} {% block section_title %}Section{% endblock %}

## {% block section_subtitle %}Détails{% endblock %}

Cette section décrit {% block section_description %}les détails spécifiques au framework{% endblock %}.
{% endblock %}

---

{% block summary_table %}
### {% block summary_title %}Résumé{% endblock %}

{% block summary_table_header %}
| Élément | Détails |
|---------|---------|
{% endblock %}
{% block summary_table_rows %}
{# Table rows go here #}
{% endblock %}
{% endblock %}

---

{% block details %}
### {% block details_title %}Détails{% endblock %}

{% block details_content %}
{# Detailed content goes here #}
{% endblock %}
{% endblock %}

---

{% block patterns %}
{% if SHOW_PATTERNS %}
### {% block patterns_title %}Modèles et Conventions{% endblock %}

{% block patterns_content %}
Les modèles suivants ont été détectés :

{% block patterns_list %}
{# Pattern list goes here #}
{% endblock %}
{% endblock %}
{% endif %}
{% endblock %}

---

{% block additional_sections %}
{# Additional framework-specific sections #}
{% endblock %}