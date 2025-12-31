# Node.js ミドルウェア & ガード セクション

## ミドルウェア設定

このセクションでは、アプリケーションで見つかったミドルウェアと認証ガードについて説明します。

### ミドルウェアチェーン

{{MIDDLEWARE_CHAIN}}

### 認証ミドルウェア

以下の認証パターンが検出されました：

{{AUTH_MIDDLEWARE}}

### Passport.js設定

{{PASSPORT_DETAILS}}

### NestJSガード

NestJSアプリケーションでは、以下のガードパターンが見つかりました：

- **@UseGuards()** - ルートまたはコントローラーにガードを適用
- **AuthGuard** - 組み込み認証ガード
- **RolesGuard** - カスタムロールベースガード

### ルート保護

{{ROUTE_PROTECTION_DETAILS}}

### CORS設定

{{CORS_DETAILS}}

### エラーハンドリングミドルウェア

{{ERROR_HANDLING}}