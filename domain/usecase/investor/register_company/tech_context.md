# 技術コンテキスト: 対象企業を登録する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Company の `driverTree` / `currentSnapshot` は [update_company_snapshot](../update_company_snapshot/tech_context.md) でも更新される。スキーマはこのファイルを正とする。

## Vault ファイル

- パス: `data/vault/companies/{id}.md`
- フィールド名は [Company ドメイン定義](../../../data/company.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
ticker: "1234"
market: "東証プライム"
sectorIds:
  - <uuid>
primarySectorId: <uuid>
name: "サンプル株式会社"
fiscalYearEnd: "03-31"
driverTree:
  - id: revenue.segmentA.volume
    label: "セグメントA 数量"
    parentId: null
    formula: null
    sectorId: null
currentSnapshot: null
createdAt: 2024-01-01T00:00:00Z
updatedAt: 2024-01-01T00:00:00Z
---

<!-- 本文: 企業概要・事業内容など、構造化しにくい背景説明（任意） -->
```

`driverTree` の要素（`DriverTreeNode`）のフィールド定義は [Company の DriverTreeNode](../../../data/company.md#drivertreenode) を参照。

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `ticker` の空文字チェック・システム全体での一意性チェック
  - `sectorIds` が1つ以上であること、各要素が既存の Sector を指すこと
  - `primarySectorId` が `sectorIds` に含まれること
- `driverTree` は指定がなければ `primarySectorId` が指す Sector の `driverTreeTemplate` をそのままコピーして初期化する（`sectorId` フィールドはコピー元がルート直下のセグメントノードに設定していればそのまま引き継ぐ）
- `currentSnapshot` は作成時 `null` で保存する
- `createdAt` と `updatedAt` は作成時同一時刻
- 書き込み後、インデックスの対応テーブルへ同期する
