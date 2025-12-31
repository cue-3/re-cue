{# Reusable component: Statistics table #}
{% if stats %}
## Estadísticas

| Métrica | Valor |
|---------|-------|
{% for key, value in stats.items() %}
| {{ key | replace('_', ' ') | title }} | {{ value }} |
{% endfor %}
{% endif %}