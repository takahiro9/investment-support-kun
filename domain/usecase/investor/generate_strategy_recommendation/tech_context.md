# 技術コンテキスト: 経営の打ち手を評価する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/strategy_recommendations/{id}.md`
- フィールド名は [StrategyRecommendation ドメイン定義](../../../data/strategy_recommendation.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
companyId: <uuid>
relatedThesisIds:
  - <uuid>
option: "サブスク転換"
executionEvidence: "過去3年でリカーリング収益比率を段階的に引き上げてきた実績があり、役員報酬にサブスク比率KPIが連動している"
executionProbability: high      # low | medium | high
impactIfExecuted: "営業利益+8〜12%（3年内）"
pricedIn: partially_priced       # not_priced | partially_priced | fully_priced
createdAt: 2024-01-01T00:00:00Z
updatedAt: 2024-01-01T00:00:00Z
---

<!-- 本文: 評価の詳しい論証（任意） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `companyId` が実在する Company を指すこと
  - `option`/`executionEvidence`/`impactIfExecuted` の空文字チェック
  - 出力文言が「A社はこうすべき」という規範的な提案文にならないよう、選択肢・根拠・確率・インパクト・織り込み度の評価という形式を崩さない（LLM生成時のプロンプト制約として実装する）
- 1回の評価リクエストにつき、選択肢の数だけ `StrategyRecommendation` を作成する
- 書き込み後、インデックスの対応テーブルへ同期する
