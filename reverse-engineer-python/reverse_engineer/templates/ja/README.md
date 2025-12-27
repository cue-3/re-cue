# 日本語テンプレート

このディレクトリには、RE-cueドキュメント生成用の日本語テンプレートが含まれています。

## 構造

- `common/` - すべてのフレームワークで使用される共通テンプレート
- `frameworks/` - フレームワーク固有のテンプレート
  - `java_spring/` - Java Spring Bootテンプレート
  - `nodejs/` - Node.js（Express、NestJS）テンプレート
  - `python/` - Python（Django、Flask、FastAPI）テンプレート

## ステータス

**翻訳保留中**：これらのテンプレートはまだ翻訳されていません。
翻訳が完了するまで、英語のテンプレートがフォールバックとして使用されます。

## 貢献

日本語翻訳に貢献するには：

1. `en/`ディレクトリから対応するテンプレートをコピーする
2. `{{VARIABLE_NAME}}`変数を保持しながらコンテンツを翻訳する
3. 翻訳を含むプルリクエストを送信する

## 使用方法

日本語テンプレートを使用するには（利用可能な場合）、次を実行します：

```bash
reverse-engineer --use-cases --template-language ja
```

または`.recue.yaml`で設定します：

```yaml
output:
  template_language: ja
```
