# Deutsche Vorlagen

Dieses Verzeichnis enthält deutsche Vorlagen für die RE-cue-Dokumentationsgenerierung.

## Struktur

- `common/` - Gemeinsame Vorlagen für alle Frameworks
- `frameworks/` - Framework-spezifische Vorlagen
  - `java_spring/` - Java Spring Boot Vorlagen
  - `nodejs/` - Node.js (Express, NestJS) Vorlagen
  - `python/` - Python (Django, Flask, FastAPI) Vorlagen

## Status

**ÜBERSETZUNG AUSSTEHEND**: Diese Vorlagen wurden noch nicht übersetzt.
Englische Vorlagen werden als Fallback verwendet, bis die Übersetzung abgeschlossen ist.

## Mitwirken

So können Sie deutsche Übersetzungen beitragen:

1. Kopieren Sie die entsprechenden Vorlagen aus dem Verzeichnis `en/`
2. Übersetzen Sie den Inhalt, behalten Sie dabei die Variablen `{{VARIABLE_NAME}}` bei
3. Reichen Sie einen Pull Request mit Ihren Übersetzungen ein

## Verwendung

Um deutsche Vorlagen zu verwenden (wenn verfügbar), führen Sie aus:

```bash
reverse-engineer --use-cases --template-language de
```

Oder konfigurieren Sie in `.recue.yaml`:

```yaml
output:
  template_language: de
```
