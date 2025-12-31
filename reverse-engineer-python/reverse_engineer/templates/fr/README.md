# Modèles en Français

Ce répertoire contient des modèles en français pour la génération de documentation RE-cue.

## Structure

- `common/` - Modèles communs utilisés dans tous les frameworks
- `frameworks/` - Modèles spécifiques au framework
  - `java_spring/` - Modèles Java Spring Boot
  - `nodejs/` - Modèles Node.js (Express, NestJS)
  - `python/` - Modèles Python (Django, Flask, FastAPI)

## Fichiers de Modèles

### Modèles Communs

- `phase1-structure.md` - Phase 1 : Analyse de la Structure du Projet
- `phase2-actors.md` - Phase 2 : Découverte des Acteurs
- `phase3-boundaries.md` - Phase 3 : Limites du Système
- `phase4-use-cases.md` - Phase 4 : Analyse des Cas d'Utilisation
- `4+1-architecture-template.md` - Modèle de Vue d'Architecture 4+1
- `base.md` - Modèle de base avec support d'héritage
- `_footer.md` - Composant de pied de page commun
- `_stats_table.md` - Composant de tableau de statistiques
- `_warning.md` - Composant de message d'avertissement

### Modèles Spécifiques au Framework

Chaque répertoire de framework contient des modèles spécialisés qui remplacent les modèles communs
avec un formatage et une terminologie spécifiques au framework.

## Utilisation

Ces modèles sont utilisés automatiquement lorsque `--template-language fr` (ou aucune langue n'est spécifiée)
est fourni à l'outil en ligne de commande RE-cue.
