---
name: list-sources
description: List all registered Sources (情報源) with their type, layer, linked reference, and fetch status, optionally filtered by layer/Company/Sector/Theme. Use when the investor wants to review the information-collection pipeline.
---

# 登録済み情報源一覧を閲覧する (List Sources)

Spec: `domain/usecase/investor/list_sources/usecase.md`

## 手順

1. 投資家に絞り込み条件が必要か確認する（任意）: `layer`、または紐づく `Company`/`Sector`/`Theme`。名前で指定された場合は `list-companies`/`list-sectors` skill で id を引く。
2. 以下を実行する:
   ```
   uv run python scripts/sources.py list [--layer "<layer>"] [--company-id "<id>"] \
     [--sector-id "<id>"] [--theme-id "<id>"]
   ```
3. stdout の JSON 配列（各要素: `id`, `type`, `layer`, `companyId`/`sectorId`/`themeId`, `name`, `url`, `description`, `status`, `lastFetchedAt`, `createdAt`, `updatedAt`）を、投資家が読みやすい表形式に整形して提示する。
4. 0件の場合は「登録済みの情報源はまだありません」と伝え、`register-source` skill での新規登録を提案する。
5. `lastFetchedAt` が `null` の Source があれば「まだ一度も取得されていません」と添える（自動取得パイプライン自体は本 skill の対象外）。

## 注意

`status=archived` の Source も一覧には含まれる。有効/無効の切り替えは本 skill の対象外。
