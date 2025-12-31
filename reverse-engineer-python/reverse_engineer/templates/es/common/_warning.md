{# Reusable component: Warning banner #}
{% if warning or warnings %}
> **⚠️ Advertencia**
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