# 技術コンテキスト: Thought を追加する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。

## Vault ファイル

- パス: `data/vault/thoughts/{id}.md`
- フィールド名は [Thought ドメイン定義](../../../data/thought.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
findingIds:
  - <uuid>
companyIds: []
sectorIds: []
themeIds: []
driverNodeIds: []
type: note              # note | question | prediction
createdAt: 2024-01-01T00:00:00Z
tags: []
---

考察・気づき・問い・予測の本文をここ（フロントマター以下）に文章で書く。
```

本文（フロントマター以下＝`body`）が考察の主役であり必須。

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `findingIds` が1つ以上であり、それぞれ実在する Finding を指すこと
  - `body` の空文字チェック
  - `driverNodeIds` を指定する場合、`companyIds` に対応する Company が含まれていること。かつ各ノードidが該当 Company の `driverTree` に実在すること
- 1つの Finding に複数の Thought を付与できる
- 書き込み後、インデックスの対応テーブルへ同期する
