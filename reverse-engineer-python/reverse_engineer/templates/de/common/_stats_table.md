{# Reusable component: Statistics table #}
{% if stats %}
## Statistiken

| Metrik | Wert |
|--------|------|
{% for key, value in stats.items() %}
| {{ key | replace('_', ' ') | title }} | {{ value }} |
{% endfor %}
{% endif %}