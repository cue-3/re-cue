# 日本語テンプレート

このディレクトリには、RE-cueドキュメント生成用の日本語テンプレートが含まれています。

## 構造

- `common/` - すべてのフレームワークで使用される共通テンプレート
- `frameworks/` - フレームワーク固有のテンプレート
  - `java_spring/` - Java Spring Bootテンプレート
  - `nodejs/` - Node.js（Express、NestJS）テンプレート
  - `python/` - Python（Django、Flask、FastAPI）テンプレート

## テンプレートファイル

### 共通テンプレート

- `phase1-structure.md` - フェーズ1：プロジェクト構造解析
- `phase2-actors.md` - フェーズ2：アクター発見
- `phase3-boundaries.md` - フェーズ3：システム境界
- `phase4-use-cases.md` - フェーズ4：ユースケース解析
- `4+1-architecture-template.md` - 4+1アーキテクチャビューテンプレート
- `base.md` - 継承サポート付きベーステンプレート
- `_footer.md` - 共通フッターコンポーネント
- `_stats_table.md` - 統計テーブルコンポーネント
- `_warning.md` - 警告メッセージコンポーネント

### フレームワーク固有テンプレート

各フレームワークディレクトリには、共通テンプレートをフレームワーク固有の
フォーマットと用語で上書きする専門テンプレートが含まれています。

## 使用方法

これらのテンプレートは、`--template-language ja`（または言語が指定されていない場合）が
RE-cueコマンドラインツールに提供された時に自動的に使用されます。
