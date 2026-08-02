# 技術コンテキスト: 情報源を登録する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/sources/{id}.md`
- フィールド名は [Source ドメイン定義](../../../data/source.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）
- `layer` に対応しない参照フィールド（例: `layer=macro` のときの `companyId`）は設定しない

## フロントマタースキーマ

```yaml
---
id: <uuid>
type: disclosure_feed   # rss_feed | web_page | youtube_channel | disclosure_feed | newsletter
layer: company           # company | sector | theme | macro
companyId: <uuid>        # layer が company の場合必須
sectorId: null            # layer が sector の場合必須
themeId: null              # layer が theme の場合必須
name: "サンプル株式会社 適時開示"
url: "https://www.release.tdnet.info/..."
description: "適時開示の一次情報を継続取得"
status: active            # active | paused | archived
lastFetchedAt: null
createdAt: 2024-01-01T00:00:00Z
updatedAt: 2024-01-01T00:00:00Z
---

<!-- 本文: Source に関するメモ（任意） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `name` の空文字チェック
  - `url` はシステム全体で一意
  - `layer` に応じて必須になる参照フィールド（[SourceLayer](../../../data/source.md#sourcelayer)）が設定されていること、参照先が実在すること
  - `url` への疎通確認（アクセス可否・種別の妥当性）。失敗時は警告のうえ登録強行を選択可能
- 作成時の `status` は `active`、`lastFetchedAt` は `null`
- 書き込み後、インデックスの対応テーブルへ同期する
