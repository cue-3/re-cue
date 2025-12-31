# Modèles RE-cue

Ce répertoire contient des modèles pour générer la documentation d'ingénierie inverse.

## Vue d'ensemble du système de modèles

RE-cue utilise le système de modèles **Jinja2** avec support pour :
- ✅ **Héritage de modèles** (`extends`) - Réutiliser la structure commune
- ✅ **Composants réutilisables** (`include`) - Partager des éléments communs
- ✅ **Rendu conditionnel** - Afficher/masquer des sections selon les données
- ✅ **Boucles** - Itérer sur des collections
- ✅ **Filtres** - Transformer les données pour l'affichage

Voir le [Guide d'héritage de modèles](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) pour plus de détails.

## Catégories de modèles

### Modèles de base (NOUVEAU dans v1.4.0)

- **`base.md`** - Modèle de base pour toute la documentation avec blocs réutilisables
- **`base_framework_section.md`** - Base pour les sections spécifiques aux frameworks

### Modèles étendus (NOUVEAU dans v1.4.0)

Modèles utilisant l'héritage pour une meilleure maintenabilité :
- **`phase1-structure-extended.md`** - Phase 1 améliorée avec héritage
- **`phase2-actors-extended.md`** - Phase 2 améliorée avec inclusions
- **`endpoint_section_extended.md`** - Section framework avec héritage

### Composants réutilisables (NOUVEAU dans v1.4.0)

Préfixés avec `_` pour une identification facile :
- **`_stats_table.md`** - Composant tableau de statistiques
- **`_footer.md`** - Pied de page du document avec informations de génération
- **`_warning.md`** - Composant bannière d'avertissement

### Modèles de phase originaux

Modèles classiques (toujours supportés pour la compatibilité ascendante) :

### Phase 1 : Structure du projet (`phase1-structure.md`)
Documente la structure de base du projet incluant :
- Points de terminaison API
- Modèles de données
- Vues UI
- Services backend
- Fonctionnalités identifiées

### Phase 2 : Découverte des acteurs (`phase2-actors.md`)
Documente les acteurs identifiés incluant :
- Utilisateurs internes
- Utilisateurs finaux
- Systèmes externes
- Niveaux d'accès et sécurité

### Phase 3 : Cartographie des frontières système (`phase3-boundaries.md`)
Documente l'architecture système incluant :
- Frontières système
- Sous-systèmes et couches
- Cartographie des composants
- Interactions entre frontières

### Phase 4 : Extraction des cas d'utilisation (`phase4-use-cases.md`)
Documente les processus métier incluant :
- Cas d'utilisation
- Relations acteur-frontière
- Règles métier
- Flux de travail
- Validation et frontières transactionnelles

## Variables de modèle

Les modèles utilisent le format de substitution suivant : `{{VARIABLE_NAME}}`

### Variables communes

- `{{PROJECT_NAME}}` - Nom du projet (kebab-case)
- `{{PROJECT_NAME_DISPLAY}}` - Nom du projet (format d'affichage)
- `{{DATE}}` - Date de génération
- `{{PROJECT_PATH}}` - Chemin absolu du projet

### Variables spécifiques aux phases

**Phase 1 :**
- `{{ENDPOINT_COUNT}}`, `{{MODEL_COUNT}}`, `{{VIEW_COUNT}}`, `{{SERVICE_COUNT}}`, `{{FEATURE_COUNT}}`
- `{{ENDPOINTS_LIST}}`, `{{MODELS_LIST}}`, `{{VIEWS_LIST}}`, `{{SERVICES_LIST}}`, `{{FEATURES_LIST}}`

**Phase 2 :**
- `{{ACTOR_COUNT}}`, `{{INTERNAL_USER_COUNT}}`, `{{END_USER_COUNT}}`, `{{EXTERNAL_SYSTEM_COUNT}}`
- `{{INTERNAL_USERS_LIST}}`, `{{END_USERS_LIST}}`, `{{EXTERNAL_SYSTEMS_LIST}}`
- `{{ACCESS_LEVELS_SUMMARY}}`, `{{SECURITY_ANNOTATIONS_SUMMARY}}`, `{{ACTOR_RELATIONSHIPS}}`

**Phase 3 :**
- `{{BOUNDARY_COUNT}}`, `{{SUBSYSTEM_COUNT}}`, `{{LAYER_COUNT}}`, `{{COMPONENT_COUNT}}`
- `{{BOUNDARIES_LIST}}`, `{{SUBSYSTEM_ARCHITECTURE}}`, `{{LAYER_ORGANIZATION}}`
- `{{COMPONENT_MAPPING}}`, `{{BOUNDARY_INTERACTIONS}}`, `{{TECH_STACK_BY_BOUNDARY}}`

**Phase 4 :**
- `{{USE_CASE_COUNT}}`, `{{ACTOR_COUNT}}`, `{{BOUNDARY_COUNT}}`
- `{{ACTORS_SUMMARY}}`, `{{BOUNDARIES_SUMMARY}}`, `{{USE_CASES_SUMMARY}}`
- `{{BUSINESS_CONTEXT}}`, `{{USE_CASES_DETAILED}}`, `{{USE_CASE_RELATIONSHIPS}}`
- `{{ACTOR_BOUNDARY_MATRIX}}`, `{{BUSINESS_RULES}}`, `{{WORKFLOWS}}`
- `{{EXTENSION_POINTS}}`, `{{VALIDATION_RULES}}`, `{{TRANSACTION_BOUNDARIES}}`

## Utilisation

Ces modèles sont utilisés par les générateurs de documents de phase dans `generators.py`. Pour modifier le format de sortie des documents de phase, éditez le fichier de modèle correspondant.

### Exemple : Personnaliser la sortie de la Phase 1

1. Éditez `phase1-structure.md`
2. Modifiez la structure, ajoutez des sections ou changez le formatage
3. Conservez les espaces réservés des variables (`{{VARIABLE}}`) intacts
4. Le générateur utilisera automatiquement le modèle mis à jour

## Héritage de modèles (ENH-TMPL-003)

### Utiliser l'héritage de modèles

**Créer un modèle personnalisé étendant la base :**

```jinja2
{% extends "base.md" %}

{% block title %}Mon Analyse - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
## Contenu personnalisé
{{ my_data }}
{% endblock %}
```

**Utiliser des composants :**

```jinja2
{% include "_stats_table.md" %}
{% include "_footer.md" %}
```

### Blocs de modèle de base disponibles

**base.md :**
- `header` - En-tête du document
- `title` - Titre uniquement
- `overview` - Section vue d'ensemble
- `overview_content` - Texte de vue d'ensemble
- `overview_stats` - Statistiques
- `main_content` - Contenu principal (à remplacer !)
- `next_steps` - Prochaines étapes
- `footer` - Pied de page

### Guide de migration

Les anciens modèles fonctionnent toujours ! Pour utiliser les nouvelles fonctionnalités :

1. **Continuer à utiliser les anciens modèles** - Aucun changement requis
2. **Créer des versions étendues** - Nouveaux modèles avec suffixe `-extended.md`
3. **Migrer progressivement** - Mettre à jour les générateurs quand vous êtes prêt

## Ressources

- [Guide d'héritage de modèles](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) - Guide complet
- [Exemples de modèles](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-EXAMPLES.md) - Exemples pratiques
- [Guide Jinja2](../../../../../docs/JINJA2-TEMPLATE-GUIDE.md) - Fonctionnalités Jinja2

---

*Fait partie de RE-cue - Boîte à outils d'ingénierie inverse*