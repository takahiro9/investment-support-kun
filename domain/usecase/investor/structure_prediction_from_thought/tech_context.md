# 技術コンテキスト: 予測を構造化する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> `Prediction` の `resolvedAt`/`outcome`/`postmortem` は [resolve_prediction](../resolve_prediction/tech_context.md) で更新される。スキーマはこのファイルを正とする。

## Vault ファイル

- パス: `data/vault/predictions/{id}.md`
- フィールド名は [Prediction ドメイン定義](../../../data/prediction.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
thesisId: <uuid>
sourceThoughtId: <uuid>
statement: "FY27Q2までに営業利益率が12%を超える"
horizon: 2027-09-30
probability: 0.6
observableText: "決算短信の営業利益率"
observableRef:               # 任意。Signal化されていなければ設定しない
  signalMetric: "operating_margin"
  comparator: ">"
  threshold: 12
  unit: "%"
resolvedAt: null
outcome: null
postmortem: null
createdAt: 2024-01-01T00:00:00Z
---

<!-- 本文: 予測の背景・前提の詳しい説明（任意） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `thesisId` が実在する Thesis を指すこと
  - `statement`/`observableText` の空文字チェック
  - `probability` は0以上1以下
  - `observableRef` を設定する場合、`signalMetric`/`comparator`/`threshold` は必須
- 作成時点では `resolvedAt`/`outcome`/`postmortem` はすべて `null`
- 書き込み後、インデックスの対応テーブルへ同期する
