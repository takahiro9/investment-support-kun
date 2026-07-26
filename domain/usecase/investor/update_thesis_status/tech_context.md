# 技術コンテキスト: 投資仮説のステータスを遷移させる

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Thesis 本体のスキーマは [create_thesis](../create_thesis/tech_context.md) を正とする。本ユースケースは既存の Thesis ファイルのうち `status` / `updatedAt`（および任意で本文への追記）のみを書き換える部分更新である。

## Vault ファイル

- パス: `data/vault/theses/{id}.md`（新規作成ではなく既存ファイルの更新）
- 更新対象フィールドは `status` と `updatedAt`。本文（論証）への追記は任意
- 他のフィールド（`consensusView`/`variant`/`whyMispriced`/`invalidation`/`confirmation`/`thoughtIds` 等）は本ユースケースでは変更しない

## 実装メモ

- `status` の遷移ルール（Python スクリプト側で実施）:
  - `status` の遷移自体を強制するステートマシンは持たない（v1では自動遷移ロジックを持たない。[Thesis の不変条件](../../../data/thesis.md#不変条件ビジネスルール)）が、`challenged` を経ずに直接 `dropped` へ遷移する操作は警告を出したうえで確認を求める
  - `dropped` への遷移には確認ステップを挟む
- `updatedAt` は更新時の現在時刻
- 書き込み後、インデックスの対応テーブルへ同期する
