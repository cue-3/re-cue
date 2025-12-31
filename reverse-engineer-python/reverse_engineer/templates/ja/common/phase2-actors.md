# フェーズ2: アクター発見
## {{PROJECT_NAME}}

**生成日**: {{DATE}}
**分析フェーズ**: 2 / 4 - アクター発見

---

## 概要

このドキュメントには、フェーズ2の分析結果が含まれています：システムと相互作用するアクターの特定（ユーザー、ロール、外部システム、サードパーティサービスを含む）。

- **アクター総数**: {{ACTOR_COUNT}}
- **内部ユーザー**: {{INTERNAL_USER_COUNT}}
- **エンドユーザー**: {{END_USER_COUNT}}
- **外部システム**: {{EXTERNAL_SYSTEM_COUNT}}

---

## アクター

| アクター | タイプ | アクセスレベル | 証拠 |
|----------|--------|----------------|------|
| {{ACTOR}} | {{ACTOR_TYPE}} | {{ACTOR_ACCESS_LEVEL}} | {{ACTOR_EVIDENCE}} |

---

## アクセスレベル

{{ACCESS_LEVELS_SUMMARY}}

---

## セキュリティアノテーション

{{SECURITY_ANNOTATIONS_SUMMARY}}

---

## アクター関係

{{ACTOR_RELATIONSHIPS}}

---

## 次のステップ

アクター分析を確認した後：

1. **フェーズ3に進む**: システム境界マッピング
   - アクターをシステム境界にマップ
   - サブシステムとレイヤーを特定
   - コンポーネントの相互作用を定義

2. **続行するコマンド**:
   ```bash
   python3 -m reverse_engineer --phase 3 --path {{PROJECT_PATH}}
   ```

---

*RE-cue - リバースエンジニアリングツールキットによって生成*