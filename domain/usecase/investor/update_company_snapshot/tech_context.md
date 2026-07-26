# 技術コンテキスト: 現在地スナップショットを更新する

> このユースケースが書き込む Vault ファイルの実装仕様。全体方針は [architecture.md](../../../../tech_context/architecture.md) を参照。
> Company 本体のスキーマは [register_company](../register_company/tech_context.md) を正とする。本ユースケースは既存の Company ファイルのうち `currentSnapshot` / `updatedAt` のみを書き換える部分更新である。

## Vault ファイル

- パス: `data/vault/companies/{id}.md`（新規作成ではなく既存ファイルの更新）
- 更新対象フィールドは `currentSnapshot` と `updatedAt` のみ。他のフィールド（`driverTree` 含む）は変更しない

## 更新後のフロントマター（該当部分）

```yaml
currentSnapshot:
  asOf: 2024-06-01
  summary: "直近四半期はセグメントAの数量が想定以上に伸長。一方で..."
updatedAt: 2024-06-01T00:00:00Z
```

## 実装メモ

- `CompanySnapshot` のフィールド定義は [Company の CompanySnapshot](../../../data/company.md#companysnapshot) を参照
- バリデーション（Python スクリプト側で実施）:
  - `summary` の空文字チェック
  - `asOf` は日付形式であること
- 要約草案生成に使う Finding / Thought の抽出は「対象 Company に紐づく Thought（`companyIds` に該当 Company を含むもの）のうち `createdAt` が前回 `currentSnapshot.asOf` より新しいもの、およびそれらが `findingIds` で参照する Finding」を対象とする
- 書き込み後、インデックス側の Company レコードも同期する
