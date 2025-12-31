# Phase 2 : Découverte des Acteurs
## {{PROJECT_NAME}}

**Généré le** : {{DATE}}
**Phase d'Analyse** : 2 sur 4 - Découverte des Acteurs

---

## Vue d'ensemble

Ce document contient les résultats de l'analyse de Phase 2 : identification des acteurs qui interagissent
avec le système, incluant les utilisateurs, les rôles, les systèmes externes et les services tiers.

- **Total des Acteurs** : {{ACTOR_COUNT}}
- **Utilisateurs Internes** : {{INTERNAL_USER_COUNT}}
- **Utilisateurs Finaux** : {{END_USER_COUNT}}
- **Systèmes Externes** : {{EXTERNAL_SYSTEM_COUNT}}

---

## Acteurs

| Acteur | Type | Niveau d'Accès | Preuve |
|--------|------|----------------|--------|
| {{ACTOR}} | {{ACTOR_TYPE}} | {{ACTOR_ACCESS_LEVEL}} | {{ACTOR_EVIDENCE}} |

---

## Niveaux d'Accès

{{ACCESS_LEVELS_SUMMARY}}

---

## Annotations de Sécurité

{{SECURITY_ANNOTATIONS_SUMMARY}}

---

## Relations entre Acteurs

{{ACTOR_RELATIONSHIPS}}

---

## Prochaines Étapes

Après avoir examiné l'analyse des acteurs :

1. **Procéder à la Phase 3** : Cartographie des Frontières du Système
   - Associer les acteurs aux frontières du système
   - Identifier les sous-systèmes et les couches
   - Définir les interactions entre composants

2. **Commande pour continuer** :
   ```bash
   python3 -m reverse_engineer --phase 3 --path {{PROJECT_PATH}}
   ```

---

*Généré par RE-cue - Boîte à Outils de Rétro-ingénierie*