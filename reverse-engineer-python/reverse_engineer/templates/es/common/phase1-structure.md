# Fase 1: Análisis de Estructura del Proyecto
## {{PROJECT_NAME}}

**Generado**: {{DATE}}
**Fase de Análisis**: 1 de 4 - Estructura del Proyecto

---

## Resumen General

Este documento contiene los resultados del análisis de la Fase 1: descubrimiento de la estructura
básica del proyecto incluyendo endpoints, modelos, vistas, servicios y características.

- **Endpoints de API**: {{ENDPOINT_COUNT}}
- **Modelos de Datos**: {{MODEL_COUNT}}
- **Vistas de UI**: {{VIEW_COUNT}}
- **Servicios Backend**: {{SERVICE_COUNT}}
- **Características**: {{FEATURE_COUNT}}

---

## Endpoints de API

| Método | Endpoint | Controlador |
|--------|----------|-------------|
| {{HTTP_METHOD}} | {{HTTP_ENDPOINT}} | {{API_CONTROLLER}} |

---

## Modelos de Datos

| Modelo | Campos | Ubicación |
|--------|--------|-----------|
| {{MODEL}} | {{FIELDS}} | {{DATA_MODEL_LOCATION}} |

---

## Vistas de UI

| Nombre de Vista | Archivo de Componente |
|-----------------|----------------------|
| {{UI_VIEW_NAME}} | {{UI_COMPONENT_FILE}} |

---

## Servicios Backend

{{SERVICES_LIST}}

---

## Características

| # | Nombre | Descripción |
|---|--------|-------------|
{{FEATURES_TABLE}}

---

## Próximos Pasos

Después de revisar este análisis de estructura:

1. **Proceder a la Fase 2**: Descubrimiento de Actores
   - Identificar usuarios, roles y sistemas externos
   - Mapear anotaciones de seguridad a actores
   - Determinar niveles de acceso

2. **Comando para continuar**:
   ```bash
   python3 -m reverse_engineer --phase 2 --path {{PROJECT_PATH}}
   ```

---

*Generado por RE-cue - Kit de Herramientas de Ingeniería Inversa*