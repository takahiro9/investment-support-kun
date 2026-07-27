---
name: update-company-snapshot
description: Refresh a Company's currentSnapshot (as-of date + summary) by reviewing the Findings/Thoughts accumulated since the last update. Use for periodic stock-taking so the investor doesn't have to re-read everything from scratch.
---

# 現在地スナップショットを更新する (Update Company Snapshot)

Spec: `domain/usecase/investor/update_company_snapshot/usecase.md`, `domain/usecase/investor/update_company_snapshot/tech_context.md`

## 手順

1. 対象 Company の id を確認する（分からなければ `list-companies`/`view-company` skill で引く）。
2. 前回スナップショット以降に蓄積された Finding/Thought を取得する:
   ```
   uv run python scripts/companies.py snapshot-context --id "<id>"
   ```
   stdout の JSON: `previousSnapshot`（前回の `asOf`/`summary`、初回は `null`）、`thoughts`（前回 `asOf` 以降に作成された、この Company に紐づく Thought）、`findings`（それらが参照する Finding）。
3. `thoughts` が0件の場合、その旨を投資家に伝え、続行するか中止するかを確認する。中止する場合はここで終了する。
4. `thoughts`/`findings` の内容をもとに要約の草案を作成し、投資家に提示する。0件、または草案作成が難しい場合は、投資家に `summary` の手入力を求める。
5. 投資家が草案を確認・編集し、最終的な `summary` を確定するまで繰り返す。
6. 確定したら、当日の日付を取得する: `date +%F`
7. 以下を実行する:
   ```
   uv run python scripts/companies.py update-snapshot --id "<id>" --as-of "<YYYY-MM-DD>" --summary "<確定した要約>"
   ```
8. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える（`summary` が空、`asOf` の形式不正など）。修正のうえ再実行する。
9. 成功時は stdout の JSON（更新後の Company）をもとに、`currentSnapshot`/`updatedAt` の更新完了を伝える。

## 注意

- このユースケースは `currentSnapshot` と `updatedAt` のみを更新する部分更新であり、`driverTree` など他のフィールドは変更しない。
- `data/vault/companies/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
