# Pythonフレームワークデコレーターセクション

## デコレーターとミドルウェア

このセクションでは、Pythonウェブアプリケーションで見つかったデコレーターとミドルウェアパターンについて説明します。

### ルートデコレーター

{{ROUTE_DECORATORS}}

### 認証デコレーター

以下の認証デコレーターが検出されました：

{{AUTH_DECORATORS}}

### 権限デコレーター

{{PERMISSION_DECORATORS}}

### Django固有のパターン

Djangoアプリケーションの場合：

- **@login_required** - ユーザー認証が必要
- **@permission_required** - 特定の権限が必要
- **@user_passes_test** - カスタム認証テスト
- **LoginRequiredMixin** - クラスベースビューのミックスイン
- **PermissionRequiredMixin** - 権限チェックのミックスイン

### Flask固有のパターン

Flaskアプリケーションの場合：

- **@login_required** - Flask-Login認証
- **@jwt_required** - Flask-JWT認証
- **@roles_required** - Flask-Securityロールチェック

### FastAPI固有のパターン

FastAPIアプリケーションの場合：

- **Depends()** - 認証のための依存性注入
- **Security()** - セキュリティスキームの依存関係
- **OAuth2PasswordBearer** - OAuth2認証

### デコレーターの順序

{{DECORATOR_ORDERING}}

### カスタムデコレーター

{{CUSTOM_DECORATORS}}