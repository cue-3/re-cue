{# Base Template for RE-cue Documentation #}
{# This template provides a consistent structure for all analysis documents #}

{% block header %}
# {% block title %}{{ PROJECT_NAME }}{% endblock %}

**Erstellt**: {{ DATE }}
{% if PHASE %}**Analysephase**: {{ PHASE }}{% endif %}
{% endblock %}

---

{% block overview %}
## Überblick

{% block overview_content %}
Dieses Dokument enthält Analyseergebnisse für {{ PROJECT_NAME }}.
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
## Nächste Schritte

Nach Durchsicht dieser Analyse:

1. **Fortfahren mit {{ NEXT_PHASE }}**
   {% block next_steps_details %}
   - Mit der nächsten Analysephase fortfahren
   {% endblock %}

{% if NEXT_COMMAND %}
2. **Befehl zum Fortfahren**:
   ```bash
   {{ NEXT_COMMAND }}
   ```
{% endif %}
{% endif %}
{% endblock %}

---

{% block footer %}
*Erstellt von RE-cue - Reverse Engineering Toolkit*
{% endblock %}