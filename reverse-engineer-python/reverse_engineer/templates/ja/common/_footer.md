{# Reusable component: Footer with generation info #}
---

**ドキュメント情報:**
- 生成日時: {{ DATE | default('Unknown') }}
{% if TOOL_VERSION %}
- ツールバージョン: {{ TOOL_VERSION }}
{% endif %}
{% if ANALYSIS_DURATION %}
- 分析時間: {{ ANALYSIS_DURATION }}
{% endif %}

*このドキュメントはRE-cue - リバースエンジニアリングツールキットによって自動生成されました*