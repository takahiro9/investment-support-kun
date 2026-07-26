# 技術コンテキスト: 時系列指標を手動で記録する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Signal は構造化データAPIからの自動取得（[fetch_signals_from_market_data](../../system/fetch_signals_from_market_data.md)）や、Findingの自然言語からのLLM抽出（[extract_signal_from_finding](../../system/extract_signal_from_finding.md)）でも生成される。スキーマはこのファイルを正とする。

## Vault ファイル

- パス: `data/vault/signals/{id}.md`
- フィールド名は [Signal ドメイン定義](../../../data/signal.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
companyId: <uuid>
category: operational      # financial | operational | leading | market
metric: "operating_margin"
period: "2027Q2"
value: 12.3
unit: "%"
sourceFindingId: <uuid>     # 任意
extractionMethod: manual     # manual | llm_extraction | structured_api
validatesThesisId: <uuid>
validatesAssumption: "サブスク転換に伴う利益率改善が想定ペースで進んでいるかの検証"
createdAt: 2024-01-01T00:00:00Z
---

<!-- 本文は基本的に使わない（時系列の1データポイントであり、論証を持たないため） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `companyId`/`validatesThesisId`/`validatesAssumption` の空文字チェック
  - `validatesThesisId` が指す Thesis の `companyId` と、Signal の `companyId` が一致すること
  - `extractionMethod = manual` の場合、`sourceFindingId` は任意
- 同一 `companyId`/`metric`/`period` の重複は上書きせず、複数の Signal として履歴に積み上げる
- 書き込み後、インデックスの対応テーブルへ同期する
