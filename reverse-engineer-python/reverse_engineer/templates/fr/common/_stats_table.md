{# Reusable component: Statistics table #}
{% if stats %}
## Statistiques

| Métrique | Valeur |
|----------|--------|
{% for key, value in stats.items() %}
| {{ key | replace('_', ' ') | title }} | {{ value }} |
{% endfor %}
{% endif %}