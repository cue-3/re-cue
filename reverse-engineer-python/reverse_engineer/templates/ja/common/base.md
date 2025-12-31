{# Base Template for RE-cue Documentation #}
{# This template provides a consistent structure for all analysis documents #}

{% block header %}
# {% block title %}{{ PROJECT_NAME }}{% endblock %}

**生成日時**: {{ DATE }}
{% if PHASE %}**分析フェーズ**: {{ PHASE }}{% endif %}
{% endblock %}

---

{% block overview %}
## 概要

{% block overview_content %}
このドキュメントには{{ PROJECT_NAME }}の分析結果が含まれています。
{% endblock %}

{% block overview_stats %}
{% endblock %}
{% endblock %}

---

{% block main_content %}
{# Main content goes here - override in child templates #}
{% endblock %}

---

{% block next_steps %}
{% if NEXT_PHASE %}
## 次のステップ

この分析を確認した後：

1. **{{ NEXT_PHASE }}に進む**
   {% block next_steps_details %}
   - 次の分析フェーズに進みます
   {% endblock %}

{% if NEXT_COMMAND %}
2. **続行するためのコマンド**：
   ```bash
   {{ NEXT_COMMAND }}
   ```
{% endif %}
{% endif %}
{% endblock %}

---

{% block footer %}
*RE-cue - リバースエンジニアリングツールキットによって生成*
{% endblock %}