# 技術コンテキスト: テーマを作成する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/themes/{id}.md`
- フィールド名は [Theme ドメイン定義](../../../data/theme.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
name: "半導体サプライチェーン再編"
description: "地政学リスクによる生産拠点の分散・国内回帰の動き"
sectorIds:
  - <uuid>
createdAt: 2024-01-01T00:00:00Z
---

<!-- 本文: テーマの背景説明（任意） -->
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `name` の空文字チェック
  - `sectorIds` の各要素が実在する Sector を指すこと、重複がないこと
- `sectorIds` は未指定なら空配列で保存する
- 書き込み後、インデックスの対応テーブルへ同期する
