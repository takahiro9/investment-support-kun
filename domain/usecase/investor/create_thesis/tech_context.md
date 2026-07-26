# 技術コンテキスト: 投資仮説を組み立てる

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Thesis の `status` は [update_thesis_status](../update_thesis_status/tech_context.md) でも更新される。スキーマはこのファイルを正とする。

## Vault ファイル

- パス: `data/vault/theses/{id}.md`
- フィールド名は [Thesis ドメイン定義](../../../data/thesis.md)（camelCase）にそのまま揃える
- datetime は ISO 8601（UTC）

## フロントマタースキーマ

```yaml
---
id: <uuid>
companyId: <uuid>
statement: "この企業はサブスク転換により利益率が構造的に改善する"
consensusView: "市場は既存のハード販売モデルの成長鈍化を織り込んでいる"
variant: "サブスク転換の進捗が市場予想より速く、利益率改善が過小評価されている"
whyMispriced: "サブスク比率がKPIとして開示されておらず、アナリストが定量化できていない"
invalidation: "サブスク比率の伸びが2四半期連続で鈍化する"
confirmation: "サブスク比率が想定を超えるペースで上昇する"
horizon: 2027-03-31
probability: 0.6
status: seed             # seed | developing | established | challenged | dropped
thoughtIds:
  - <uuid>
createdAt: 2024-01-01T00:00:00Z
updatedAt: 2024-01-01T00:00:00Z
tags: []
---

仮説の論証本文。なぜ束ねたThought群からこのstatementが立つのか、その組み立てを文章で綴る。
```

## 実装メモ

- UUID は呼び出し側（skill の `uuidgen`）で生成して Python スクリプトに渡す
- バリデーション（Python スクリプト側で実施）:
  - `companyId` が実在する Company を指すこと
  - `statement`/`consensusView`/`variant`/`whyMispriced`/`invalidation`/`confirmation`/`body` の空文字チェック
  - `thoughtIds` の各要素が実在する Thought を指すこと（重複不可）
  - `probability` を指定する場合は0以上1以下
- 作成時の `status` は常に `seed`。`status` の遷移は本ユースケースでは行わない（[update_thesis_status](../update_thesis_status/usecase.md)が担う）
- `createdAt` と `updatedAt` は作成時同一時刻
- 書き込み後、インデックスの対応テーブルへ同期する
