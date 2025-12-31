{% extends "base.md" %}

{% block title %}フェーズ1: プロジェクト構造分析 - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
このドキュメントには、フェーズ1の分析結果が含まれています：エンドポイント、モデル、ビュー、サービス、機能を含むプロジェクトの基本構造の発見。
{% endblock %}

{% block overview_stats %}
- **APIエンドポイント**: {{ ENDPOINT_COUNT | default(0) }}
- **データモデル**: {{ MODEL_COUNT | default(0) }}
- **UIビュー**: {{ VIEW_COUNT | default(0) }}
- **バックエンドサービス**: {{ SERVICE_COUNT | default(0) }}
- **機能**: {{ FEATURE_COUNT | default(0) }}
{% endblock %}

{% block main_content %}
## APIエンドポイント

{% if ENDPOINT_COUNT and ENDPOINT_COUNT > 0 %}
| メソッド | エンドポイント | コントローラー |
|--------|----------|------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} |
{% endfor %}
{% else %}
*APIエンドポイントは検出されませんでした。*
{% endif %}

---

## データモデル

{% if MODEL_COUNT and MODEL_COUNT > 0 %}
| モデル | フィールド | 場所 |
|-------|--------|----------|
{% for model in models %}
| {{ model.name }} | {{ model.fields | length }} | {{ model.location }} |
{% endfor %}
{% else %}
*データモデルは検出されませんでした。*
{% endif %}

---

## UIビュー

{% if VIEW_COUNT and VIEW_COUNT > 0 %}
| ビュー名 | コンポーネントファイル |
|-----------|----------------|
{% for view in views %}
| {{ view.name }} | {{ view.file }} |
{% endfor %}
{% else %}
*UIビューは検出されませんでした。*
{% endif %}

---

## バックエンドサービス

{% if services %}
{% for service in services %}
### {{ service.name }}

- **タイプ**: {{ service.type }}
- **場所**: {{ service.location }}
{% if service.methods %}
- **メソッド**: {{ service.methods | length }}
{% endif %}

{% endfor %}
{% else %}
*バックエンドサービスは検出されませんでした。*
{% endif %}

---

## 機能

{% if features %}
以下の機能が特定されました：

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description | default('説明なし') }}
{% endfor %}
{% else %}
*機能は検出されませんでした。*
{% endif %}
{% endblock %}

{% block next_steps_details %}
- システムと対話するアクターを特定する
- ユーザーロールと権限を発見する
- 外部システムと統合をマッピングする
{% endblock %}