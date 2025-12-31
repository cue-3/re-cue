{# Base Template for Framework-Specific Sections #}
{# This template provides a consistent structure for framework sections #}

{% block section_header %}
# {% block framework_name %}Framework{% endblock %} {% block section_title %}セクション{% endblock %}

## {% block section_subtitle %}詳細{% endblock %}

このセクションでは{% block section_description %}フレームワーク固有の詳細{% endblock %}について説明します。
{% endblock %}

---

{% block summary_table %}
### {% block summary_title %}概要{% endblock %}

{% block summary_table_header %}
| 項目 | 詳細 |
|------|------|
{% endblock %}
{% block summary_table_rows %}
{# Table rows go here #}
{% endblock %}
{% endblock %}

---

{% block details %}
### {% block details_title %}詳細{% endblock %}

{% block details_content %}
{# Detailed content goes here #}
{% endblock %}
{% endblock %}

---

{% block patterns %}
{% if SHOW_PATTERNS %}
### {% block patterns_title %}パターンと規約{% endblock %}

{% block patterns_content %}
以下のパターンが検出されました：

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