# Plantillas en Español

Este directorio contiene plantillas en español para la generación de documentación de RE-cue.

## Estructura

- `common/` - Plantillas comunes utilizadas en todos los frameworks
- `frameworks/` - Plantillas específicas del framework
  - `java_spring/` - Plantillas de Java Spring Boot
  - `nodejs/` - Plantillas de Node.js (Express, NestJS)
  - `python/` - Plantillas de Python (Django, Flask, FastAPI)

## Estado

**PENDIENTE DE TRADUCCIÓN**: Estas plantillas aún no se han traducido. 
Se utilizarán las plantillas en inglés como alternativa hasta que se complete la traducción.

## Contribuir

Para contribuir con traducciones al español:

1. Copie las plantillas correspondientes del directorio `en/`
2. Traduzca el contenido manteniendo las variables `{{VARIABLE_NAME}}`
3. Envíe un pull request con sus traducciones

## Uso

Para usar plantillas en español (cuando estén disponibles), ejecute:

```bash
reverse-engineer --use-cases --template-language es
```

O configure en `.recue.yaml`:

```yaml
output:
  template_language: es
```
