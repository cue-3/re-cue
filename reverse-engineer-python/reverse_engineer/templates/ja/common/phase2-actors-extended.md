{% extends "base.md" %}

{% block title %}フェーズ2: アクター発見 - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
このドキュメントには、フェーズ2分析の結果が含まれています：システムと相互作用するアクターの特定、
ユーザー、ロール、外部システム、サードパーティサービスを含みます。
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
{% include "_warning.md" %}

## アクター

{% if actors and actors | length > 0 %}
| アクター | タイプ | アクセスレベル | 証拠 |
|----------|--------|----------------|------|
{% for actor in actors %}
| {{ actor.name }} | {{ actor.type }} | {{ actor.access_level | default('N/A') }} | {{ actor.evidence | default('N/A') }} |
{% endfor %}

### アクター詳細

{% for actor in actors %}
#### {{ actor.name }}

- **タイプ**: {{ actor.type }}
- **アクセスレベル**: {{ actor.access_level | default('未指定') }}
{% if actor.permissions %}
- **権限**: {{ actor.permissions | join(', ') }}
{% endif %}
{% if actor.description %}
- **説明**: {{ actor.description }}
{% endif %}

{% endfor %}
{% else %}
*まだアクターは特定されていません。*
{% endif %}

---

## アクセスレベル

{% if access_levels %}
以下のアクセスレベルが検出されました：

{% for level in access_levels %}
- **{{ level.name }}**: {{ level.description | default('説明なし') }}
  - アクター数: {{ level.actor_count | default(0) }}
{% endfor %}
{% else %}
{{ ACCESS_LEVELS_SUMMARY | default('*アクセスレベル情報は利用できません*') }}
{% endif %}

---

## セキュリティアノテーション

{% if security_annotations %}
{% for annotation in security_annotations %}
- **{{ annotation.type }}**: {{ annotation.count }}回使用
{% if annotation.examples %}
  - 例: {{ annotation.examples | join(', ') }}
{% endif %}
{% endfor %}
{% else %}
{{ SECURITY_ANNOTATIONS_SUMMARY | default('*セキュリティアノテーションは検出されませんでした*') }}
{% endif %}

---

## アクター関係

{% if actor_relationships %}
{{ actor_relationships }}
{% else %}
{{ ACTOR_RELATIONSHIPS | default('*アクター関係はマッピングされていません*') }}
{% endif %}
{% endblock %}

{% block next_steps_details %}
- システム境界のマッピング
- サブシステムとレイヤーの特定
- コンポーネント相互作用の文書化
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}