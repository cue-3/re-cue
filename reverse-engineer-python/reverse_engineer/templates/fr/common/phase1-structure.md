# Phase 1 : Analyse de la Structure du Projet
## {{PROJECT_NAME}}

**Généré le** : {{DATE}}
**Phase d'analyse** : 1 sur 4 - Structure du Projet

---

## Vue d'ensemble

Ce document contient les résultats de l'analyse de Phase 1 : découverte de la structure
de base du projet incluant les points de terminaison, modèles, vues, services et fonctionnalités.

- **Points de terminaison API** : {{ENDPOINT_COUNT}}
- **Modèles de données** : {{MODEL_COUNT}}
- **Vues UI** : {{VIEW_COUNT}}
- **Services Backend** : {{SERVICE_COUNT}}
- **Fonctionnalités** : {{FEATURE_COUNT}}

---

## Points de terminaison API

| Méthode | Point de terminaison | Contrôleur |
|---------|---------------------|------------|
| {{HTTP_METHOD}} | {{HTTP_ENDPOINT}} | {{API_CONTROLLER}} |

---

## Modèles de données

| Modèle | Champs | Emplacement |
|--------|--------|-------------|
| {{MODEL}} | {{FIELDS}} | {{DATA_MODEL_LOCATION}} |

---

## Vues UI

| Nom de la vue | Fichier du composant |
|---------------|---------------------|
| {{UI_VIEW_NAME}} | {{UI_COMPONENT_FILE}} |

---

## Services Backend

{{SERVICES_LIST}}

---

## Fonctionnalités

| # | Nom | Description |
|---|-----|-------------|
{{FEATURES_TABLE}}

---

## Prochaines étapes

Après avoir examiné cette analyse de structure :

1. **Passer à la Phase 2** : Découverte des Acteurs
   - Identifier les utilisateurs, rôles et systèmes externes
   - Mapper les annotations de sécurité aux acteurs
   - Déterminer les niveaux d'accès

2. **Commande pour continuer** :
   ```bash
   python3 -m reverse_engineer --phase 2 --path {{PROJECT_PATH}}
   ```

---

*Généré par RE-cue - Boîte à outils d'ingénierie inverse*