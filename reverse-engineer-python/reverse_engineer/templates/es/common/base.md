{# Base Template for RE-cue Documentation #}
{# This template provides a consistent structure for all analysis documents #}

{% block header %}
# {% block title %}{{ PROJECT_NAME }}{% endblock %}

**Generado**: {{ DATE }}
{% if PHASE %}**Fase de Análisis**: {{ PHASE }}{% endif %}
{% endblock %}

---

{% block overview %}
## Resumen General

{% block overview_content %}
Este documento contiene los resultados del análisis para {{ PROJECT_NAME }}.
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
## Próximos Pasos

Después de revisar este análisis:

1. **Proceder a {{ NEXT_PHASE }}**
   {% block next_steps_details %}
   - Continuar con la siguiente fase de análisis
   {% endblock %}

{% if NEXT_COMMAND %}
2. **Comando para continuar**:
   ```bash
   {{ NEXT_COMMAND }}
   ```
{% endif %}
{% endif %}
{% endblock %}

---

{% block footer %}
*Generado por RE-cue - Kit de Herramientas de Ingeniería Inversa*
{% endblock %}