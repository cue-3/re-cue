{# Reusable component: Footer with generation info #}
---

**Dokumentinformationen:**
- Erstellt: {{ DATE | default('Unknown') }}
{% if TOOL_VERSION %}
- Tool-Version: {{ TOOL_VERSION }}
{% endif %}
{% if ANALYSIS_DURATION %}
- Analysedauer: {{ ANALYSIS_DURATION }}
{% endif %}

*Dieses Dokument wurde automatisch von RE-cue - Reverse Engineering Toolkit erstellt*