{# Reusable component: Footer with generation info #}
---

**Informations du Document :**
- Généré le : {{ DATE | default('Unknown') }}
{% if TOOL_VERSION %}
- Version de l'Outil : {{ TOOL_VERSION }}
{% endif %}
{% if ANALYSIS_DURATION %}
- Durée de l'Analyse : {{ ANALYSIS_DURATION }}
{% endif %}

*Ce document a été généré automatiquement par RE-cue - Reverse Engineering Toolkit*