{# Base Template for Framework-Specific Sections #}
{# This template provides a consistent structure for framework sections #}

{% block section_header %}
# {% block framework_name %}Framework{% endblock %} {% block section_title %}Section{% endblock %}

## {% block section_subtitle %}Details{% endblock %}

This section describes {% block section_description %}the framework-specific details{% endblock %}.
{% endblock %}

---

{% block summary_table %}
### {% block summary_title %}Summary{% endblock %}

{% block summary_table_header %}
| Item | Details |
|------|---------|
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
### {% block patterns_title %}Patterns and Conventions{% endblock %}

{% block patterns_content %}
The following patterns were detected:

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
