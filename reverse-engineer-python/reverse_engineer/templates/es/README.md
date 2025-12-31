# Plantillas en Español

Este directorio contiene plantillas en español para la generación de documentación de RE-cue.

## Estructura

- `common/` - Plantillas comunes utilizadas en todos los frameworks
- `frameworks/` - Plantillas específicas del framework
  - `java_spring/` - Plantillas de Java Spring Boot
  - `nodejs/` - Plantillas de Node.js (Express, NestJS)
  - `python/` - Plantillas de Python (Django, Flask, FastAPI)

## Archivos de Plantilla

### Plantillas Comunes

- `phase1-structure.md` - Fase 1: Análisis de Estructura del Proyecto
- `phase2-actors.md` - Fase 2: Descubrimiento de Actores
- `phase3-boundaries.md` - Fase 3: Límites del Sistema
- `phase4-use-cases.md` - Fase 4: Análisis de Casos de Uso
- `4+1-architecture-template.md` - Plantilla de Vista de Arquitectura 4+1
- `base.md` - Plantilla base con soporte de herencia
- `_footer.md` - Componente de pie de página común
- `_stats_table.md` - Componente de tabla de estadísticas
- `_warning.md` - Componente de mensaje de advertencia

### Plantillas Específicas del Framework

Cada directorio de framework contiene plantillas especializadas que sobrescriben las plantillas comunes
con formato y terminología específicos del framework.

## Uso

Estas plantillas se usan automáticamente cuando se proporciona `--template-language es` (o no se especifica idioma)
a la herramienta de línea de comandos RE-cue.
