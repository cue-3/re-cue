# Fase 2: Descubrimiento de Actores
## {{PROJECT_NAME}}

**Generado**: {{DATE}}
**Fase de Análisis**: 2 de 4 - Descubrimiento de Actores

---

## Resumen General

Este documento contiene los resultados del análisis de la Fase 2: identificación de actores que interactúan
con el sistema, incluyendo usuarios, roles, sistemas externos y servicios de terceros.

- **Total de Actores**: {{ACTOR_COUNT}}
- **Usuarios Internos**: {{INTERNAL_USER_COUNT}}
- **Usuarios Finales**: {{END_USER_COUNT}}
- **Sistemas Externos**: {{EXTERNAL_SYSTEM_COUNT}}

---

## Actores

| Actor | Tipo | Nivel de Acceso | Evidencia |
|-------|------|-----------------|-----------|
| {{ACTOR}} | {{ACTOR_TYPE}} | {{ACTOR_ACCESS_LEVEL}} | {{ACTOR_EVIDENCE}} |

---

## Niveles de Acceso

{{ACCESS_LEVELS_SUMMARY}}

---

## Anotaciones de Seguridad

{{SECURITY_ANNOTATIONS_SUMMARY}}

---

## Relaciones entre Actores

{{ACTOR_RELATIONSHIPS}}

---

## Próximos Pasos

Después de revisar el análisis de actores:

1. **Proceder a la Fase 3**: Mapeo de Límites del Sistema
   - Mapear actores a límites del sistema
   - Identificar subsistemas y capas
   - Definir interacciones entre componentes

2. **Comando para continuar**:
   ```bash
   python3 -m reverse_engineer --phase 3 --path {{PROJECT_PATH}}
   ```

---

*Generado por RE-cue - Kit de Herramientas de Ingeniería Inversa*