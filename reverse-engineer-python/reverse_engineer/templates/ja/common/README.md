# RE-cue テンプレート

このディレクトリには、リバースエンジニアリングドキュメントを生成するためのテンプレートが含まれています。

## テンプレートシステムの概要

RE-cueは**Jinja2**テンプレートを使用し、以下をサポートしています：
- ✅ **テンプレート継承** (`extends`) - 共通構造の再利用
- ✅ **再利用可能なコンポーネント** (`include`) - 共通要素の共有
- ✅ **条件付きレンダリング** - データに基づいてセクションの表示/非表示
- ✅ **ループ** - コレクションの反復処理
- ✅ **フィルター** - 表示用のデータ変換

詳細は[テンプレート継承ガイド](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md)を参照してください。

## テンプレートカテゴリー

### ベーステンプレート（v1.4.0の新機能）

- **`base.md`** - 再利用可能なブロックを持つすべてのドキュメントのベーステンプレート
- **`base_framework_section.md`** - フレームワーク固有セクションのベース

### 拡張テンプレート（v1.4.0の新機能）

保守性向上のために継承を使用するテンプレート：
- **`phase1-structure-extended.md`** - 継承を使用した拡張フェーズ1
- **`phase2-actors-extended.md`** - インクルードを使用した拡張フェーズ2
- **`endpoint_section_extended.md`** - 継承を使用したフレームワークセクション

### 再利用可能なコンポーネント（v1.4.0の新機能）

識別しやすいように`_`で始まる：
- **`_stats_table.md`** - 統計テーブルコンポーネント
- **`_footer.md`** - 生成情報を含むドキュメントフッター
- **`_warning.md`** - 警告バナーコンポーネント

### オリジナルフェーズテンプレート

クラシックテンプレート（後方互換性のため引き続きサポート）：

### フェーズ1：プロジェクト構造（`phase1-structure.md`）
以下を含む基本的なプロジェクト構造を文書化：
- APIエンドポイント
- データモデル
- UIビュー
- バックエンドサービス
- 識別された機能

### フェーズ2：アクター発見（`phase2-actors.md`）
以下を含む識別されたアクターを文書化：
- 内部ユーザー
- エンドユーザー
- 外部システム
- アクセスレベルとセキュリティ

### フェーズ3：システム境界マッピング（`phase3-boundaries.md`）
以下を含むシステムアーキテクチャを文書化：
- システム境界
- サブシステムとレイヤー
- コンポーネントマッピング
- 境界間の相互作用

### フェーズ4：ユースケース抽出（`phase4-use-cases.md`）
以下を含むビジネスプロセスを文書化：
- ユースケース
- アクター・境界の関係
- ビジネスルール
- ワークフロー
- 検証とトランザクション境界

## テンプレート変数

テンプレートは以下のプレースホルダー形式を使用します：`{{VARIABLE_NAME}}`

### 共通変数

- `{{PROJECT_NAME}}` - プロジェクト名（ケバブケース）
- `{{PROJECT_NAME_DISPLAY}}` - プロジェクト名（表示形式）
- `{{DATE}}` - 生成日
- `{{PROJECT_PATH}}` - 絶対プロジェクトパス

### フェーズ固有の変数

**フェーズ1：**
- `{{ENDPOINT_COUNT}}`, `{{MODEL_COUNT}}`, `{{VIEW_COUNT}}`, `{{SERVICE_COUNT}}`, `{{FEATURE_COUNT}}`
- `{{ENDPOINTS_LIST}}`, `{{MODELS_LIST}}`, `{{VIEWS_LIST}}`, `{{SERVICES_LIST}}`, `{{FEATURES_LIST}}`

**フェーズ2：**
- `{{ACTOR_COUNT}}`, `{{INTERNAL_USER_COUNT}}`, `{{END_USER_COUNT}}`, `{{EXTERNAL_SYSTEM_COUNT}}`
- `{{INTERNAL_USERS_LIST}}`, `{{END_USERS_LIST}}`, `{{EXTERNAL_SYSTEMS_LIST}}`
- `{{ACCESS_LEVELS_SUMMARY}}`, `{{SECURITY_ANNOTATIONS_SUMMARY}}`, `{{ACTOR_RELATIONSHIPS}}`

**フェーズ3：**
- `{{BOUNDARY_COUNT}}`, `{{SUBSYSTEM_COUNT}}`, `{{LAYER_COUNT}}`, `{{COMPONENT_COUNT}}`
- `{{BOUNDARIES_LIST}}`, `{{SUBSYSTEM_ARCHITECTURE}}`, `{{LAYER_ORGANIZATION}}`
- `{{COMPONENT_MAPPING}}`, `{{BOUNDARY_INTERACTIONS}}`, `{{TECH_STACK_BY_BOUNDARY}}`

**フェーズ4：**
- `{{USE_CASE_COUNT}}`, `{{ACTOR_COUNT}}`, `{{BOUNDARY_COUNT}}`
- `{{ACTORS_SUMMARY}}`, `{{BOUNDARIES_SUMMARY}}`, `{{USE_CASES_SUMMARY}}`
- `{{BUSINESS_CONTEXT}}`, `{{USE_CASES_DETAILED}}`, `{{USE_CASE_RELATIONSHIPS}}`
- `{{ACTOR_BOUNDARY_MATRIX}}`, `{{BUSINESS_RULES}}`, `{{WORKFLOWS}}`
- `{{EXTENSION_POINTS}}`, `{{VALIDATION_RULES}}`, `{{TRANSACTION_BOUNDARIES}}`

## 使用方法

これらのテンプレートは`generators.py`のフェーズドキュメントジェネレーターによって使用されます。フェーズドキュメントの出力形式を変更するには、対応するテンプレートファイルを編集してください。

### 例：フェーズ1出力のカスタマイズ

1. `phase1-structure.md`を編集
2. 構造を変更、セクションを追加、またはフォーマットを変更
3. 変数プレースホルダー（`{{VARIABLE}}`）はそのまま保持
4. ジェネレーターは自動的に更新されたテンプレートを使用

## テンプレート継承（ENH-TMPL-003）

### テンプレート継承の使用

**ベースを拡張するカスタムテンプレートの作成：**

```jinja2
{% extends "base.md" %}

{% block title %}私の分析 - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
## カスタムコンテンツ
{{ my_data }}
{% endblock %}
```

**コンポーネントの使用：**

```jinja2
{% include "_stats_table.md" %}
{% include "_footer.md" %}
```

### 利用可能なベーステンプレートブロック

**base.md：**
- `header` - ドキュメントヘッダー
- `title` - タイトルのみ
- `overview` - 概要セクション
- `overview_content` - 概要テキスト
- `overview_stats` - 統計
- `main_content` - メインコンテンツ（これをオーバーライド！）
- `next_steps` - 次のステップ
- `footer` - フッター

### 移行ガイド

古いテンプレートは引き続き動作します！新機能を使用するには：

1. **古いテンプレートを使い続ける** - 変更不要
2. **拡張バージョンを作成** - `-extended.md`接尾辞を持つ新しいテンプレート
3. **段階的に移行** - 準備ができたらジェネレーターを更新

## リソース

- [テンプレート継承ガイド](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) - 完全ガイド
- [テンプレート例](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-EXAMPLES.md) - 実践的な例
- [Jinja2ガイド](../../../../../docs/JINJA2-TEMPLATE-GUIDE.md) - Jinja2機能

---

*RE-cue - リバースエンジニアリングツールキットの一部*