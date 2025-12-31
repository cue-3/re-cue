{# Reusable component: Statistics table #}
{% if stats %}
## 統計

| メトリック | 値 |
|-----------|-----|
{% for key, value in stats.items() %}
| {{ key | replace('_', ' ') | title }} | {{ value }} |
{% endfor %}
{% endif %}