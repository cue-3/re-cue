# Plantillas RE-cue

Este directorio contiene plantillas para generar documentación de ingeniería inversa.

## Resumen del Sistema de Plantillas

RE-cue utiliza plantillas **Jinja2** con soporte para:
- ✅ **Herencia de Plantillas** (`extends`) - Reutilizar estructura común
- ✅ **Componentes Reutilizables** (`include`) - Compartir elementos comunes
- ✅ **Renderizado Condicional** - Mostrar/ocultar secciones según los datos
- ✅ **Bucles** - Iterar sobre colecciones
- ✅ **Filtros** - Transformar datos para visualización

Consulte la [Guía de Herencia de Plantillas](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) para más detalles.

## Categorías de Plantillas

### Plantillas Base (NUEVO en v1.4.0)

- **`base.md`** - Plantilla base para toda la documentación con bloques reutilizables
- **`base_framework_section.md`** - Base para secciones específicas del framework

### Plantillas Extendidas (NUEVO en v1.4.0)

Plantillas que utilizan herencia para mejor mantenibilidad:
- **`phase1-structure-extended.md`** - Fase 1 mejorada con herencia
- **`phase2-actors-extended.md`** - Fase 2 mejorada con includes
- **`endpoint_section_extended.md`** - Sección de framework con herencia

### Componentes Reutilizables (NUEVO en v1.4.0)

Con prefijo `_` para fácil identificación:
- **`_stats_table.md`** - Componente de tabla de estadísticas
- **`_footer.md`** - Pie de documento con información de generación
- **`_warning.md`** - Componente de banner de advertencia

### Plantillas de Fase Originales

Plantillas clásicas (aún soportadas para compatibilidad hacia atrás):

### Fase 1: Estructura del Proyecto (`phase1-structure.md`)
Documenta la estructura básica del proyecto incluyendo:
- Endpoints API
- Modelos de datos
- Vistas UI
- Servicios backend
- Características identificadas

### Fase 2: Descubrimiento de Actores (`phase2-actors.md`)
Documenta los actores identificados incluyendo:
- Usuarios internos
- Usuarios finales
- Sistemas externos
- Niveles de acceso y seguridad

### Fase 3: Mapeo de Límites del Sistema (`phase3-boundaries.md`)
Documenta la arquitectura del sistema incluyendo:
- Límites del sistema
- Subsistemas y capas
- Mapeo de componentes
- Interacciones entre límites

### Fase 4: Extracción de Casos de Uso (`phase4-use-cases.md`)
Documenta los procesos de negocio incluyendo:
- Casos de uso
- Relaciones actor-límite
- Reglas de negocio
- Flujos de trabajo
- Validación y límites transaccionales

## Variables de Plantilla

Las plantillas utilizan el siguiente formato de marcador: `{{VARIABLE_NAME}}`

### Variables Comunes

- `{{PROJECT_NAME}}` - Nombre del proyecto (kebab-case)
- `{{PROJECT_NAME_DISPLAY}}` - Nombre del proyecto (formato de visualización)
- `{{DATE}}` - Fecha de generación
- `{{PROJECT_PATH}}` - Ruta absoluta del proyecto

### Variables Específicas por Fase

**Fase 1:**
- `{{ENDPOINT_COUNT}}`, `{{MODEL_COUNT}}`, `{{VIEW_COUNT}}`, `{{SERVICE_COUNT}}`, `{{FEATURE_COUNT}}`
- `{{ENDPOINTS_LIST}}`, `{{MODELS_LIST}}`, `{{VIEWS_LIST}}`, `{{SERVICES_LIST}}`, `{{FEATURES_LIST}}`

**Fase 2:**
- `{{ACTOR_COUNT}}`, `{{INTERNAL_USER_COUNT}}`, `{{END_USER_COUNT}}`, `{{EXTERNAL_SYSTEM_COUNT}}`
- `{{INTERNAL_USERS_LIST}}`, `{{END_USERS_LIST}}`, `{{EXTERNAL_SYSTEMS_LIST}}`
- `{{ACCESS_LEVELS_SUMMARY}}`, `{{SECURITY_ANNOTATIONS_SUMMARY}}`, `{{ACTOR_RELATIONSHIPS}}`

**Fase 3:**
- `{{BOUNDARY_COUNT}}`, `{{SUBSYSTEM_COUNT}}`, `{{LAYER_COUNT}}`, `{{COMPONENT_COUNT}}`
- `{{BOUNDARIES_LIST}}`, `{{SUBSYSTEM_ARCHITECTURE}}`, `{{LAYER_ORGANIZATION}}`
- `{{COMPONENT_MAPPING}}`, `{{BOUNDARY_INTERACTIONS}}`, `{{TECH_STACK_BY_BOUNDARY}}`

**Fase 4:**
- `{{USE_CASE_COUNT}}`, `{{ACTOR_COUNT}}`, `{{BOUNDARY_COUNT}}`
- `{{ACTORS_SUMMARY}}`, `{{BOUNDARIES_SUMMARY}}`, `{{USE_CASES_SUMMARY}}`
- `{{BUSINESS_CONTEXT}}`, `{{USE_CASES_DETAILED}}`, `{{USE_CASE_RELATIONSHIPS}}`
- `{{ACTOR_BOUNDARY_MATRIX}}`, `{{BUSINESS_RULES}}`, `{{WORKFLOWS}}`
- `{{EXTENSION_POINTS}}`, `{{VALIDATION_RULES}}`, `{{TRANSACTION_BOUNDARIES}}`

## Uso

Estas plantillas son utilizadas por los generadores de documentos de fase en `generators.py`. Para modificar el formato de salida de los documentos de fase, edite el archivo de plantilla correspondiente.

### Ejemplo: Personalizar la Salida de la Fase 1

1. Edite `phase1-structure.md`
2. Modifique la estructura, agregue secciones o cambie el formato
3. Mantenga intactos los marcadores de variables (`{{VARIABLE}}`)
4. El generador utilizará automáticamente la plantilla actualizada

## Herencia de Plantillas (ENH-TMPL-003)

### Usando Herencia de Plantillas

**Crear una plantilla personalizada extendiendo la base:**

```jinja2
{% extends "base.md" %}

{% block title %}Mi Análisis - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
## Contenido Personalizado
{{ my_data }}
{% endblock %}
```

**Usando componentes:**

```jinja2
{% include "_stats_table.md" %}
{% include "_footer.md" %}
```

### Bloques Disponibles en la Plantilla Base

**base.md:**
- `header` - Encabezado del documento
- `title` - Solo título
- `overview` - Sección de resumen
- `overview_content` - Texto del resumen
- `overview_stats` - Estadísticas
- `main_content` - Contenido principal (¡sobrescribir esto!)
- `next_steps` - Próximos pasos
- `footer` - Pie de página

### Guía de Migración

¡Las plantillas antiguas siguen funcionando! Para usar las nuevas características:

1. **Seguir usando plantillas antiguas** - No se requiere cambio
2. **Crear versiones extendidas** - Nuevas plantillas con sufijo `-extended.md`
3. **Migrar gradualmente** - Actualizar generadores cuando esté listo

## Recursos

- [Guía de Herencia de Plantillas](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) - Guía completa
- [Ejemplos de Plantillas](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-EXAMPLES.md) - Ejemplos prácticos
- [Guía Jinja2](../../../../../docs/JINJA2-TEMPLATE-GUIDE.md) - Características de Jinja2

---

*Parte de RE-cue - Kit de Herramientas de Ingeniería Inversa*