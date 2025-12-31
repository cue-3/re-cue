{# Base Template for RE-cue Documentation #}
{# This template provides a consistent structure for all analysis documents #}

{% block header %}
# {% block title %}{{ PROJECT_NAME }}{% endblock %}

**Généré le** : {{ DATE }}
{% if PHASE %}**Phase d'Analyse** : {{ PHASE }}{% endif %}
{% endblock %}

---

{% block overview %}
## Vue d'Ensemble

{% block overview_content %}
Ce document contient les résultats d'analyse pour {{ PROJECT_NAME }}.
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
## Prochaines Étapes

Après avoir examiné cette analyse :

1. **Procéder à {{ NEXT_PHASE }}**
   {% block next_steps_details %}
   - Continuer avec la prochaine phase d'analyse
   {% endblock %}

{% if NEXT_COMMAND %}
2. **Commande pour continuer** :
   ```bash
   {{ NEXT_COMMAND }}
   ```
{% endif %}
{% endif %}
{% endblock %}

---

{% block footer %}
*Généré par RE-cue - Boîte à Outils d'Ingénierie Inverse*
{% endblock %}