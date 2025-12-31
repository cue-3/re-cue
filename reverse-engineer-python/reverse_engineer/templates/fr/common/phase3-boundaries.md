# Phase 3 : Cartographie des Frontières du Système
## {{PROJECT_NAME}}

**Généré le** : {{DATE}}
**Phase d'Analyse** : 3 sur 4 - Cartographie des Frontières du Système

---

## Vue d'Ensemble

Ce document contient les résultats de l'analyse de la Phase 3 : cartographie des frontières du système,
des sous-systèmes, des couches et des interactions entre composants.

- **Frontières du Système** : {{BOUNDARY_COUNT}}
- **Sous-systèmes** : {{SUBSYSTEM_COUNT}}
- **Couches** : {{LAYER_COUNT}}
- **Composants** : {{COMPONENT_COUNT}}

---

## Frontières du Système

| Frontière du Système | Type | Nombre de Composants | Composants Clés |
|---------------------|------|---------------------|-----------------|
{{BOUNDARIES_TABLE}}

---

## Architecture des Sous-systèmes

| Sous-système | Composants | Interfaces | Liste des Composants |
|--------------|------------|------------|---------------------|
{{SUBSYSTEM_ARCHITECTURE}}

---

## Organisation des Couches

{{LAYER_ORGANIZATION}}

---

## Cartographie des Composants

{{COMPONENT_MAPPING}}

---

## Interactions entre Frontières

{{BOUNDARY_INTERACTIONS}}

---

## Pile Technologique par Frontière

{{TECH_STACK_BY_BOUNDARY}}

---

## Prochaines Étapes

Après avoir examiné la cartographie des frontières :

1. **Passer à la Phase 4** : Extraction des Cas d'Utilisation
   - Identifier les cas d'utilisation à partir des interactions acteur-frontière
   - Extraire les processus métier
   - Documenter les scénarios et les flux de travail

2. **Commande pour continuer** :
   ```bash
   python3 -m reverse_engineer --phase 4 --path {{PROJECT_PATH}}
   ```

---

*Généré par RE-cue - Boîte à Outils d'Ingénierie Inverse*