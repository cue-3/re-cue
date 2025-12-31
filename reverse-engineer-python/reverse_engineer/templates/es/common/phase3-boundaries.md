# Fase 3: Mapeo de Límites del Sistema
## {{PROJECT_NAME}}

**Generado**: {{DATE}}
**Fase de Análisis**: 3 de 4 - Mapeo de Límites del Sistema

---

## Resumen

Este documento contiene los resultados del análisis de la Fase 3: mapeo de límites del sistema,
subsistemas, capas e interacciones entre componentes.

- **Límites del Sistema**: {{BOUNDARY_COUNT}}
- **Subsistemas**: {{SUBSYSTEM_COUNT}}
- **Capas**: {{LAYER_COUNT}}
- **Componentes**: {{COMPONENT_COUNT}}

---

## Límites del Sistema

| Límite del Sistema | Tipo | Cantidad de Componentes | Componentes Clave |
|--------------------|------|-------------------------|-------------------|
{{BOUNDARIES_TABLE}}

---

## Arquitectura de Subsistemas

| Subsistema | Componentes | Interfaces | Lista de Componentes |
|------------|-------------|------------|----------------------|
{{SUBSYSTEM_ARCHITECTURE}}

---

## Organización por Capas

{{LAYER_ORGANIZATION}}

---

## Mapeo de Componentes

{{COMPONENT_MAPPING}}

---

## Interacciones entre Límites

{{BOUNDARY_INTERACTIONS}}

---

## Stack Tecnológico por Límite

{{TECH_STACK_BY_BOUNDARY}}

---

## Próximos Pasos

Después de revisar el mapeo de límites:

1. **Proceder a la Fase 4**: Extracción de Casos de Uso
   - Identificar casos de uso a partir de las interacciones actor-límite
   - Extraer procesos de negocio
   - Documentar escenarios y flujos de trabajo

2. **Comando para continuar**:
   ```bash
   python3 -m reverse_engineer --phase 4 --path {{PROJECT_PATH}}
   ```

---

*Generado por RE-cue - Kit de Herramientas de Ingeniería Inversa*