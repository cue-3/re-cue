{# Base Template for Framework-Specific Sections #}
{# This template provides a consistent structure for framework sections #}

{% block section_header %}
# {% block framework_name %}Framework{% endblock %} {% block section_title %}Sección{% endblock %}

## {% block section_subtitle %}Detalles{% endblock %}

Esta sección describe {% block section_description %}los detalles específicos del framework{% endblock %}.
{% endblock %}

---

{% block summary_table %}
### {% block summary_title %}Resumen{% endblock %}

{% block summary_table_header %}
| Elemento | Detalles |
|----------|----------|
{% endblock %}
{% block summary_table_rows %}
{# Table rows go here #}
{% endblock %}
{% endblock %}

---

{% block details %}
### {% block details_title %}Detalles{% endblock %}

{% block details_content %}
{# Detailed content goes here #}
{% endblock %}
{% endblock %}

---

{% block patterns %}
{% if SHOW_PATTERNS %}
### {% block patterns_title %}Patrones y Convenciones{% endblock %}

{% block patterns_content %}
Se detectaron los siguientes patrones:

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