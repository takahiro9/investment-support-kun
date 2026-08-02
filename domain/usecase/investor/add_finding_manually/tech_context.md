# 技術コンテキスト: Finding を手動で追加する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Finding は自動取得（[fetch_findings_from_sources](../../system/fetch_findings_from_sources.md)）でも生成される。スキーマはこのファイルを正とする。

## Vault ファイル

- パス: `data/vault/findings/{id}.md`
- フィールド名は [Finding ドメイン定義](../../../data/finding.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
type: disclosure        # web_article | memo | pdf | youtube | image | disclosure | link
title: "2026年6月期 第1四半期決算短信"
url: "https://..."       # web_article / youtube / disclosure / link の場合は必須
sourceUrl: "https://..."
evidenceTier: primary_disclosure   # primary_disclosure | company_issued | third_party | inference
savedAt: 2024-01-01T00:00:00Z
contentUpdatedAt: 2024-01-01T00:00:00Z   # 情報源が提供する更新日時。不明なら null
tags: []
---

<!-- 本文: 記事・資料の抜粋・整理。type が memo の場合の本文はここに記述する -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `type` が `web_article` / `youtube` / `disclosure` / `link` の場合、`url` 必須
  - `type` が `memo` の場合、本文（`body`）必須
  - `evidenceTier` は必須。省略不可
  - 同一 `url` のFindingは重複登録不可（システム全体で一意）
- 書き込み後、インデックスの対応テーブルへ同期する
