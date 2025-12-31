{# Base Template for Framework-Specific Sections #}
{# This template provides a consistent structure for framework sections #}

{% block section_header %}
# {% block framework_name %}Framework{% endblock %} {% block section_title %}Abschnitt{% endblock %}

## {% block section_subtitle %}Details{% endblock %}

Dieser Abschnitt beschreibt {% block section_description %}die Framework-spezifischen Details{% endblock %}.
{% endblock %}

---

{% block summary_table %}
### {% block summary_title %}Zusammenfassung{% endblock %}

{% block summary_table_header %}
| Element | Details |
|---------|---------|
{% endblock %}
{% block summary_table_rows %}
{# Table rows go here #}
{% endblock %}
{% endblock %}

---

{% block details %}
### {% block details_title %}Details{% endblock %}

{% block details_content %}
{# Detailed content goes here #}
{% endblock %}
{% endblock %}

---

{% block patterns %}
{% if SHOW_PATTERNS %}
### {% block patterns_title %}Muster und Konventionen{% endblock %}

{% block patterns_content %}
Die folgenden Muster wurden erkannt:

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