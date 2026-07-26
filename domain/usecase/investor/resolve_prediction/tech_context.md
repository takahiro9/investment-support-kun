# 技術コンテキスト: 予測の答え合わせをする

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Prediction 本体のスキーマは [structure_prediction_from_thought](../structure_prediction_from_thought/tech_context.md) を正とする。本ユースケースは既存の Prediction ファイルのうち `resolvedAt`/`outcome`/`postmortem` のみを書き換える部分更新である。

## Vault ファイル

- パス: `data/vault/predictions/{id}.md`（新規作成ではなく既存ファイルの更新）
- 更新対象フィールドは `resolvedAt`/`outcome`/`postmortem`。他のフィールドは変更しない

## 更新後のフロントマター（該当部分）

```yaml
resolvedAt: 2027-10-05T00:00:00Z
outcome: hit          # hit | miss | ambiguous
postmortem: null       # outcome が miss / ambiguous の場合は必須
```

## 実装メモ

- バリデーション（Python スクリプト側で実施）:
  - 対象 Prediction の `resolvedAt` が未設定であること（二重の答え合わせ防止）
  - `outcome` が `miss` または `ambiguous` の場合、`postmortem` の空文字チェックを必須とする
- `observableRef` が設定されている場合の自動判定候補は、`companyId`（Prediction が属する Thesis の `companyId`）・`metric = observableRef.signalMetric`・`period` が `horizon` に対応する `Signal` を検索し、`observableRef.comparator`/`threshold` と比較して算出する
- 書き込み後、インデックスの対応テーブルへ同期する
