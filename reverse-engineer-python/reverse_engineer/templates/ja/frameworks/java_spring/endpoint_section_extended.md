{% extends "base_framework_section.md" %}

{% block framework_name %}Java Spring Boot{% endblock %}
{% block section_title %}エンドポイントセクション{% endblock %}
{% block section_subtitle %}APIエンドポイント{% endblock %}

{% block section_description %}Spring BootアプリケーションでディスカバリーされたREST APIエンドポイント{% endblock %}

{% block summary_title %}エンドポイントサマリー{% endblock %}

{% block summary_table_header %}
| メソッド | パス | コントローラー | 認証 | 説明 |
|----------|------|----------------|------|------|
{% endblock %}

{% block summary_table_rows %}
{% if endpoints %}
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} | {% if endpoint.authenticated %}🔒 必要{% else %}不要{% endif %} | {{ endpoint.description | default('N/A') }} |
{% endfor %}
{% else %}
{{ ENDPOINT_ROWS | default('*エンドポイントが見つかりません*') }}
{% endif %}
{% endblock %}

{% block details_title %}エンドポイント詳細{% endblock %}

{% block details_content %}
{% if endpoints %}
{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

- **コントローラー**: {{ endpoint.controller }}
- **メソッド**: {{ endpoint.handler_method | default('N/A') }}
{% if endpoint.authenticated %}
- **認証**: 必要 ({{ endpoint.auth_type | default('Spring Security') }})
{% endif %}
{% if endpoint.parameters %}
- **パラメータ**:
{% for param in endpoint.parameters %}
  - `{{ param.name }}` ({{ param.type }}){% if param.required %} - 必須{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
{{ ENDPOINT_DETAILS | default('*詳細なエンドポイント情報はありません*') }}
{% endif %}
{% endblock %}

{% block patterns_title %}使用されているSpringアノテーション{% endblock %}

{% block patterns_content %}
コードベースで以下のSpringアノテーションが検出されました：

{% block spring_annotations %}
- **@RestController** - クラスをRESTコントローラーとしてマーク
- **@RequestMapping** - HTTPリクエストをハンドラーメソッドにマッピング
- **@GetMapping** - HTTP GETリクエストを処理
- **@PostMapping** - HTTP POSTリクエストを処理
- **@PutMapping** - HTTP PUTリクエストを処理
- **@DeleteMapping** - HTTP DELETEリクエストを処理
- **@PatchMapping** - HTTP PATCHリクエストを処理
{% endblock %}
{% endblock %}

{% block additional_sections %}
### リクエストマッピングパターン

{% if request_mappings %}
{% for mapping in request_mappings %}
- **{{ mapping.pattern }}**: {{ mapping.count }}個のエンドポイントで使用
{% endfor %}
{% else %}
{{ REQUEST_MAPPING_DETAILS | default('*リクエストマッピングパターンは検出されませんでした*') }}
{% endif %}

---

### レスポンスタイプ

{% if response_types %}
{% for response in response_types %}
- **{{ response.type }}**: {{ response.count }}個のエンドポイントから返却
{% endfor %}
{% else %}
{{ RESPONSE_TYPE_DETAILS | default('*レスポンスタイプ情報はありません*') }}
{% endif %}
{% endblock %}