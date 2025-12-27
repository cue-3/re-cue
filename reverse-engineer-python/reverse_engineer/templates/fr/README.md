# Modèles en Français

Ce répertoire contient des modèles en français pour la génération de documentation RE-cue.

## Structure

- `common/` - Modèles communs utilisés dans tous les frameworks
- `frameworks/` - Modèles spécifiques au framework
  - `java_spring/` - Modèles Java Spring Boot
  - `nodejs/` - Modèles Node.js (Express, NestJS)
  - `python/` - Modèles Python (Django, Flask, FastAPI)

## Statut

**EN ATTENTE DE TRADUCTION** : Ces modèles n'ont pas encore été traduits.
Les modèles anglais seront utilisés comme solution de repli jusqu'à ce que la traduction soit terminée.

## Contribuer

Pour contribuer aux traductions françaises :

1. Copiez les modèles correspondants du répertoire `en/`
2. Traduisez le contenu en conservant les variables `{{VARIABLE_NAME}}`
3. Soumettez une pull request avec vos traductions

## Utilisation

Pour utiliser les modèles français (lorsqu'ils seront disponibles), exécutez :

```bash
reverse-engineer --use-cases --template-language fr
```

Ou configurez dans `.recue.yaml` :

```yaml
output:
  template_language: fr
```
