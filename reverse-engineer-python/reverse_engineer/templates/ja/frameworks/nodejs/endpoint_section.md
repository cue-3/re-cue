# Node.js/Express エンドポイントセクション

## APIルート

このセクションでは、Express/NestJSアプリケーションで発見されたHTTPルートについて説明します。

### ルート概要

| メソッド | パス | ハンドラー | ミドルウェア | 説明 |
|----------|------|------------|--------------|------|
{{ROUTE_ROWS}}

### ルート詳細

{{ROUTE_DETAILS}}

### Expressルートパターン

以下のExpressルートパターンが検出されました：

```javascript
// Express route handlers
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
```

### NestJSデコレーター

NestJSアプリケーションでは、以下のデコレーターが見つかりました：

- **@Controller()** - コントローラークラスを定義
- **@Get()** - HTTP GETリクエストを処理
- **@Post()** - HTTP POSTリクエストを処理
- **@Put()** - HTTP PUTリクエストを処理
- **@Delete()** - HTTP DELETEリクエストを処理

### ミドルウェアスタック

{{MIDDLEWARE_DETAILS}}

### ルートパラメータ

{{ROUTE_PARAMETERS}}