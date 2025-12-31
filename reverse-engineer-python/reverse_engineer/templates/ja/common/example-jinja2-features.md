# Jinja2による拡張テンプレート例

このテンプレートは、Jinja2統合によって実現される高度な機能を示しています。

## プロジェクト: {{ project_name | upper }}

**生成日時**: {{ date }}
**バージョン**: {{ version | default('1.0.0') }}

---

## 機能概要

{% if actor_count > 0 %}
### アクター (合計{{ actor_count }}個)

このプロジェクトでは{{ actor_count }}個のアクター{% if actor_count != 1 %}{% endif %}が識別されました：

{% for actor in actors %}
- **{{ actor.name }}** ({{ actor.type | replace('_', ' ') | title }})
  - アクセスレベル: {{ actor.access_level }}
  {% if actor.description %}
  - 説明: {{ actor.description }}
  {% endif %}
{% endfor %}
{% else %}
*まだアクターは識別されていません。*
{% endif %}

---

{% if endpoints %}
## APIエンドポイント ({{ endpoints | length }}個)

以下のエンドポイントが利用可能です：

| メソッド | パス | 認証必須 | 説明 |
|----------|------|----------|------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {% if endpoint.authenticated %}🔒 はい{% else %}いいえ{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}

### エンドポイント統計

- 総エンドポイント数: {{ endpoints | length }}
- 認証必須エンドポイント: {{ endpoints | selectattr('authenticated') | list | length }}
- パブリックエンドポイント: {{ endpoints | rejectattr('authenticated') | list | length }}

### 使用されているHTTPメソッド

{% for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}**: {{ count }}個のエンドポイント{% if count != 1 %}{% endif %}
{% endif %}
{% endfor %}

{% else %}
*このプロジェクトではエンドポイントが発見されませんでした。*
{% endif %}

---

{% if models %}
## データモデル ({{ models | length }}個)

{% for model in models %}
### {{ loop.index }}. {{ model.name }}

- **フィールド**: {{ model.fields }}
- **場所**: `{{ model.location }}`
{% if model.relationships %}
- **リレーションシップ**: {{ model.relationships | join(', ') }}
{% endif %}

{% endfor %}
{% else %}
*データモデルが見つかりませんでした。*
{% endif %}

---

## 品質メトリクス

{% if test_coverage %}
### テストカバレッジ

- 全体: {{ test_coverage.overall }}%
{% if test_coverage.overall >= 80 %}
- ステータス: ✅ **優秀** - よくテストされたコードベース
{% elif test_coverage.overall >= 60 %}
- ステータス: ⚠️ **良好** - さらにテストを追加することを検討してください
{% else %}
- ステータス: ❌ **改善が必要** - テストカバレッジが低い
{% endif %}
{% endif %}

{% if code_quality %}
### コード品質

{% for metric, value in code_quality.items() %}
- {{ metric | replace('_', ' ') | title }}: {{ value }}
{% endfor %}
{% endif %}

---

## 推奨事項

{% if recommendations %}
{% for category, items in recommendations.items() %}
### {{ category | title }}

{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{% endfor %}
{% else %}
*現時点では推奨事項はありません。*
{% endif %}

---

## サマリー

この分析で発見されたもの：
{% if actor_count > 0 %}- {{ actor_count }}個のアクター{% endif %}
{% if endpoints %}- {{ endpoints | length }}個のAPIエンドポイント{% endif %}
{% if models %}- {{ models | length }}個のデータモデル{% endif %}

{% if actor_count == 0 and (endpoints | length) == 0 and (models | length) == 0 %}
*プロジェクト分析は未完了です。完全な分析を実行してください。*
{% else %}
*分析完了。詳細情報については上記のセクションを確認してください。*
{% endif %}

---

*Jinja2テンプレート機能を使用したRE-cueによって生成*