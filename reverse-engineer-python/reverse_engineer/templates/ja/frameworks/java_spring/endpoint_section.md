# Java Spring Boot エンドポイントセクション

## APIエンドポイント

このセクションでは、Spring Bootアプリケーションで発見されたREST APIエンドポイントについて説明します。

### エンドポイント概要

| メソッド | パス | コントローラー | 認証 | 説明 |
|----------|------|----------------|------|------|
{{ENDPOINT_ROWS}}

### エンドポイント詳細

{{ENDPOINT_DETAILS}}

### 使用されているSpringアノテーション

コードベースで以下のSpringアノテーションが検出されました：

- **@RestController** - クラスをRESTコントローラーとしてマークします
- **@RequestMapping** - HTTPリクエストをハンドラーメソッドにマッピングします
- **@GetMapping** - HTTP GETリクエストを処理します
- **@PostMapping** - HTTP POSTリクエストを処理します
- **@PutMapping** - HTTP PUTリクエストを処理します
- **@DeleteMapping** - HTTP DELETEリクエストを処理します
- **@PatchMapping** - HTTP PATCHリクエストを処理します

### リクエストマッピングパターン

{{REQUEST_MAPPING_DETAILS}}

### レスポンスタイプ

{{RESPONSE_TYPE_DETAILS}}