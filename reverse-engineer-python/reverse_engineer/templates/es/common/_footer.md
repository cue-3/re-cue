{# Reusable component: Footer with generation info #}
---

**Información del Documento:**
- Generado: {{ DATE | default('Unknown') }}
{% if TOOL_VERSION %}
- Versión de la Herramienta: {{ TOOL_VERSION }}
{% endif %}
{% if ANALYSIS_DURATION %}
- Duración del Análisis: {{ ANALYSIS_DURATION }}
{% endif %}

*Este documento fue generado automáticamente por RE-cue - Reverse Engineering Toolkit*