{# Reusable component: Warning banner #}
{% if warning or warnings %}
> **⚠️ Avertissement**
> 
{% if warning %}
> {{ warning }}
{% endif %}
{% if warnings %}
{% for w in warnings %}
> - {{ w }}
{% endfor %}
{% endif %}
>

{% endif %}