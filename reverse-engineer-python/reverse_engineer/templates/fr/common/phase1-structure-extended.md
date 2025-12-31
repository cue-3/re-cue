{% extends "base.md" %}

{% block title %}Phase 1 : Analyse de la Structure du Projet - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
Ce document contient les résultats de l'analyse de la Phase 1 : découverte de la structure
de base du projet incluant les points de terminaison, les modèles, les vues, les services et les fonctionnalités.
{% endblock %}

{% block overview_stats %}
- **Points de Terminaison API** : {{ ENDPOINT_COUNT | default(0) }}
- **Modèles de Données** : {{ MODEL_COUNT | default(0) }}
- **Vues UI** : {{ VIEW_COUNT | default(0) }}
- **Services Backend** : {{ SERVICE_COUNT | default(0) }}
- **Fonctionnalités** : {{ FEATURE_COUNT | default(0) }}
{% endblock %}

{% block main_content %}
## Points de Terminaison API

{% if ENDPOINT_COUNT and ENDPOINT_COUNT > 0 %}
| Méthode | Point de Terminaison | Contrôleur |
|---------|---------------------|------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} |
{% endfor %}
{% else %}
*Aucun point de terminaison API détecté.*
{% endif %}

---

## Modèles de Données

{% if MODEL_COUNT and MODEL_COUNT > 0 %}
| Modèle | Champs | Emplacement |
|--------|--------|-------------|
{% for model in models %}
| {{ model.name }} | {{ model.fields | length }} | {{ model.location }} |
{% endfor %}
{% else %}
*Aucun modèle de données détecté.*
{% endif %}

---

## Vues UI

{% if VIEW_COUNT and VIEW_COUNT > 0 %}
| Nom de la Vue | Fichier du Composant |
|---------------|---------------------|
{% for view in views %}
| {{ view.name }} | {{ view.file }} |
{% endfor %}
{% else %}
*Aucune vue UI détectée.*
{% endif %}

---

## Services Backend

{% if services %}
{% for service in services %}
### {{ service.name }}

- **Type** : {{ service.type }}
- **Emplacement** : {{ service.location }}
{% if service.methods %}
- **Méthodes** : {{ service.methods | length }}
{% endif %}

{% endfor %}
{% else %}
*Aucun service backend détecté.*
{% endif %}

---

## Fonctionnalités

{% if features %}
Les fonctionnalités suivantes ont été identifiées :

{% for feature in features %}
- **{{ feature.name }}** : {{ feature.description | default('Aucune description') }}
{% endfor %}
{% else %}
*Aucune fonctionnalité détectée.*
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Identifier les acteurs qui interagissent avec le système
- Découvrir les rôles et permissions des utilisateurs
- Cartographier les systèmes externes et les intégrations
{% endblock %}