{# Reusable component: Statistics table #}
{% if stats %}
## Statistics

| Metric | Value |
|--------|-------|
{% for key, value in stats.items() %}
| {{ key | replace('_', ' ') | title }} | {{ value }} |
{% endfor %}
{% endif %}
