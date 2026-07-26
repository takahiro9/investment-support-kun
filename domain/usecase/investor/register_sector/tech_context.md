# 技術コンテキスト: 業種を登録する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/sectors/{id}.md`
- フィールド名は [Sector ドメイン定義](../../../data/sector.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
name: "半導体製造装置"
driverTreeTemplate:
  - id: revenue.segmentA.volume
    label: "セグメントA 数量"
    parentId: null
    formula: null
createdAt: 2024-01-01T00:00:00Z
---

<!-- 本文: 業種の背景説明（任意） -->
```

`driverTreeTemplate` の要素（`DriverTreeNode`）のフィールド定義は [Company の DriverTreeNode](../../../data/company.md#drivertreenode) を参照。Sectorのテンプレートには `sectorId` フィールドは持たせない（Sector自身が業種を表すため）。

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `name` の空文字チェック
  - システム全体で `name` が重複していないこと
- `driverTreeTemplate` が未指定の場合は空配列として保存する
- 書き込み後、インデックスの対応テーブルへ同期する（Vault からの再構築でも復元可能）
