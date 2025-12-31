# Exemple de Modèle Amélioré avec Jinja2

Ce modèle démontre les capacités avancées rendues possibles par l'intégration de Jinja2.

## Projet : {{ project_name | upper }}

**Généré** : {{ date }}
**Version** : {{ version | default('1.0.0') }}

---

## Résumé des Fonctionnalités

{% if actor_count > 0 %}
### Acteurs ({{ actor_count }} au total)

Ce projet a identifié {{ actor_count }} acteur{% if actor_count != 1 %}s{% endif %} :

{% for actor in actors %}
- **{{ actor.name }}** ({{ actor.type | replace('_', ' ') | title }})
  - Niveau d'Accès : {{ actor.access_level }}
  {% if actor.description %}
  - Description : {{ actor.description }}
  {% endif %}
{% endfor %}
{% else %}
*Aucun acteur n'a encore été identifié.*
{% endif %}

---

{% if endpoints %}
## Points de Terminaison API ({{ endpoints | length }})

Les points de terminaison suivants sont disponibles :

| Méthode | Chemin | Authentifié | Description |
|---------|--------|-------------|-------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {% if endpoint.authenticated %}🔒 Oui{% else %}Non{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}

### Statistiques des Points de Terminaison

- Total des points de terminaison : {{ endpoints | length }}
- Points de terminaison authentifiés : {{ endpoints | selectattr('authenticated') | list | length }}
- Points de terminaison publics : {{ endpoints | rejectattr('authenticated') | list | length }}

### Méthodes HTTP Utilisées

{% for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}** : {{ count }} point{% if count != 1 %}s{% endif %} de terminaison
{% endif %}
{% endfor %}

{% else %}
*Aucun point de terminaison découvert dans ce projet.*
{% endif %}

---

{% if models %}
## Modèles de Données ({{ models | length }})

{% for model in models %}
### {{ loop.index }}. {{ model.name }}

- **Champs** : {{ model.fields }}
- **Emplacement** : `{{ model.location }}`
{% if model.relationships %}
- **Relations** : {{ model.relationships | join(', ') }}
{% endif %}

{% endfor %}
{% else %}
*Aucun modèle de données trouvé.*
{% endif %}

---

## Métriques de Qualité

{% if test_coverage %}
### Couverture de Tests

- Globale : {{ test_coverage.overall }}%
{% if test_coverage.overall >= 80 %}
- Statut : ✅ **Excellent** - Base de code bien testée
{% elif test_coverage.overall >= 60 %}
- Statut : ⚠️ **Bon** - Envisagez d'ajouter plus de tests
{% else %}
- Statut : ❌ **Nécessite des Améliorations** - Faible couverture de tests
{% endif %}
{% endif %}

{% if code_quality %}
### Qualité du Code

{% for metric, value in code_quality.items() %}
- {{ metric | replace('_', ' ') | title }} : {{ value }}
{% endfor %}
{% endif %}

---

## Recommandations

{% if recommendations %}
{% for category, items in recommendations.items() %}
### {{ category | title }}

{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{% endfor %}
{% else %}
*Aucune recommandation pour le moment.*
{% endif %}

---

## Résumé

Cette analyse a trouvé :
{% if actor_count > 0 %}- {{ actor_count }} acteur(s){% endif %}
{% if endpoints %}- {{ endpoints | length }} point(s) de terminaison API{% endif %}
{% if models %}- {{ models | length }} modèle(s) de données{% endif %}

{% if actor_count == 0 and (endpoints | length) == 0 and (models | length) == 0 %}
*L'analyse du projet est incomplète. Veuillez exécuter une analyse complète.*
{% else %}
*Analyse terminée. Consultez les sections ci-dessus pour des informations détaillées.*
{% endif %}

---

*Généré par RE-cue avec modélisation Jinja2*