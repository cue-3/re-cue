"""
Internationalization (i18n) support for generated documentation.

Provides translations for hardcoded strings in generated documentation.
"""

# Translation dictionaries for supported languages
TRANSLATIONS = {
    "en": {
        # Use case labels
        "primary_actor": "Primary Actor",
        "secondary_actors": "Secondary Actors",
        "preconditions": "Preconditions",
        "postconditions": "Postconditions",
        "main_scenario": "Main Scenario",
        "extensions": "Extensions",
        "use_cases": "Use Cases",
        "total": "Total",
        
        # Business context
        "transaction_boundaries": "Transaction Boundaries",
        "write": "Write",
        "read_only": "Read-Only",
        "validation_rules": "Validation Rules",
        "constraints": "constraints",
        "business_workflows": "Business Workflows",
        "patterns": "patterns",
        "business_rules": "Business Rules",
        "derived": "derived",
    },
    "de": {
        # Use case labels
        "primary_actor": "Hauptakteur",
        "secondary_actors": "Nebenakteure",
        "preconditions": "Vorbedingungen",
        "postconditions": "Nachbedingungen",
        "main_scenario": "Hauptszenario",
        "extensions": "Erweiterungen",
        "use_cases": "Anwendungsfälle",
        "total": "Gesamt",
        
        # Business context
        "transaction_boundaries": "Transaktionsgrenzen",
        "write": "Schreiben",
        "read_only": "Nur Lesen",
        "validation_rules": "Validierungsregeln",
        "constraints": "Einschränkungen",
        "business_workflows": "Geschäftsprozesse",
        "patterns": "Muster",
        "business_rules": "Geschäftsregeln",
        "derived": "abgeleitet",
    },
    "es": {
        # Use case labels
        "primary_actor": "Actor Principal",
        "secondary_actors": "Actores Secundarios",
        "preconditions": "Precondiciones",
        "postconditions": "Postcondiciones",
        "main_scenario": "Escenario Principal",
        "extensions": "Extensiones",
        "use_cases": "Casos de Uso",
        "total": "Total",
        
        # Business context
        "transaction_boundaries": "Límites de Transacción",
        "write": "Escritura",
        "read_only": "Solo Lectura",
        "validation_rules": "Reglas de Validación",
        "constraints": "restricciones",
        "business_workflows": "Flujos de Trabajo",
        "patterns": "patrones",
        "business_rules": "Reglas de Negocio",
        "derived": "derivadas",
    },
    "fr": {
        # Use case labels
        "primary_actor": "Acteur Principal",
        "secondary_actors": "Acteurs Secondaires",
        "preconditions": "Préconditions",
        "postconditions": "Postconditions",
        "main_scenario": "Scénario Principal",
        "extensions": "Extensions",
        "use_cases": "Cas d'Utilisation",
        "total": "Total",
        
        # Business context
        "transaction_boundaries": "Limites de Transaction",
        "write": "Écriture",
        "read_only": "Lecture Seule",
        "validation_rules": "Règles de Validation",
        "constraints": "contraintes",
        "business_workflows": "Flux de Travail",
        "patterns": "modèles",
        "business_rules": "Règles Métier",
        "derived": "dérivées",
    },
    "ja": {
        # Use case labels
        "primary_actor": "主要アクター",
        "secondary_actors": "副次アクター",
        "preconditions": "前提条件",
        "postconditions": "事後条件",
        "main_scenario": "主要シナリオ",
        "extensions": "拡張",
        "use_cases": "ユースケース",
        "total": "合計",
        
        # Business context
        "transaction_boundaries": "トランザクション境界",
        "write": "書き込み",
        "read_only": "読み取り専用",
        "validation_rules": "検証ルール",
        "constraints": "制約",
        "business_workflows": "ビジネスワークフロー",
        "patterns": "パターン",
        "business_rules": "ビジネスルール",
        "derived": "派生",
    },
}


def get_text(key: str, language: str = "en") -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: Translation key
        language: Target language code (en, de, es, fr, ja)
        
    Returns:
        Translated string, or the key itself if not found
    """
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
