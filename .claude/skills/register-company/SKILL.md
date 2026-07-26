---
name: register-company
description: Register a new Company (対象企業) in the investment vault, initializing its driver tree from the primary sector's template. Use when the investor wants to start tracking a new investment target.
---

# 対象企業を登録する (Register Company)

Spec: `domain/usecase/investor/register_company/usecase.md`, `domain/usecase/investor/register_company/tech_context.md`

## 事前条件

`primarySectorId` に指定する Sector が既に登録されていること。存在しない場合は先に `register-sector` skill を案内する。Sector の一覧・IDは `list-sectors` skill (`uv run python scripts/sectors.py list`) で確認できる。

## 手順

1. 投資家から以下を確認する:
   - `ticker`（証券コード、必須）
   - `market`（市場区分、必須。例: "東証プライム"）
   - `name`（企業名、必須）
   - `fiscalYearEnd`（決算期、必須。例: "03-31"）
   - `sectorIds`（実質的な事業を持つ Sector、1つ以上。Sector名で聞いた場合は `list-sectors` の結果から id を引く）
   - `primarySectorId`（`sectorIds` のいずれか1つ、ヘッドライン分類）
2. UUID を生成する: `uuidgen`
3. 以下を実行する:
   ```
   uv run python scripts/companies.py register --id <uuid生成結果> --ticker "<ticker>" \
     --market "<market>" --name "<name>" --fiscal-year-end "<fiscalYearEnd>" \
     --sector-ids "<id1>,<id2>,..." --primary-sector-id "<primarySectorId>" \
     [--driver-tree '<JSON配列>'] [--body "<任意の本文>"]
   ```
   `--driver-tree` を省略すると、`primarySectorId` が指す Sector の `driverTreeTemplate` が自動でコピーされる。
4. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝え、再入力を促す。よくある失敗:
   - `ticker` が空、または既に登録済み
   - `sectorIds` が空、または `primarySectorId` が `sectorIds` に含まれない
   - `primarySectorId` の Sector が存在しない
5. 成功時は stdout の JSON（登録された Company とコピーされた `driverTree`）をもとに、登録完了を投資家に伝える。

## 注意

- `data/vault/companies/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
