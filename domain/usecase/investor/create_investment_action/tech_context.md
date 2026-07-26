# 技術コンテキスト: 投資家自身の打ち手を記録する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/investment_actions/{id}.md`
- フィールド名は [InvestmentAction ドメイン定義](../../../data/investment_action.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
companyId: <uuid>
relatedThesisIds:
  - <uuid>
relatedStrategyRecommendationIds:
  - <uuid>
action: add                 # entry | add | hold | reduce | exit
positionSizingRationale: "確度0.6・invalidation発生時の想定損失-15%を踏まえ、ポートフォリオの3%まで積み増す"
positionSizePercent: 3
nextResearch: "サブスク比率のセグメント別内訳（ドライバーツリー: revenue.segmentA.subscriptionRatio）の解消"
bearCase: "サブスク転換が競合の値下げ攻勢により想定より遅延するリスクがある"
createdAt: 2024-01-01T00:00:00Z
updatedAt: 2024-01-01T00:00:00Z
---

<!-- 本文: 判断の詳しい論証（任意） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `companyId` が実在する Company を指すこと
  - `positionSizingRationale`/`nextResearch` の空文字チェック
  - `relatedThesisIds`/`relatedStrategyRecommendationIds` の各要素が実在すること
- `bearCase` は空文字列可（未生成・スキップ時）。ただし空の場合、一覧・詳細表示側で「Red Team未実施」であることを明示する
- 書き込み後、インデックスの対応テーブルへ同期する
