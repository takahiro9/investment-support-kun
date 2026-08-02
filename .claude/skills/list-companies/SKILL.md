---
name: list-companies
description: List all registered Companies (対象企業), optionally filtered by Sector. Use when the investor wants to review or compare tracked companies.
---

# 対象企業一覧を閲覧する (List Companies)

Spec: `domain/usecase/investor/list_companies/usecase.md`

## 手順

1. 投資家に業種（Sector）による絞り込みが必要か確認する（任意）。Sector名で指定された場合は `list-sectors` skill で id を引く。
2. 以下を実行する:
   ```
   uv run python scripts/companies.py list [--sector-id "<sectorId>"]
   ```
3. stdout の JSON 配列（各要素: `id`, `ticker`, `market`, `name`, `sectorIds`, `primarySectorId`, `fiscalYearEnd`, `createdAt`, `updatedAt`）を、投資家が読みやすい表形式に整形して提示する。
4. 0件の場合は「登録済みの対象企業はまだありません」と伝え、`register-company` skill での新規登録を提案する。

## 注意

`currentSnapshot`（現在地スナップショット）はこのコマンドの出力には含まれない（インデックスの集計対象外）。個社の詳細は `view-company` skill の対象。
