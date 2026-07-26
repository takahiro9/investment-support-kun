---
name: list-sectors
description: List all registered Sectors (業種) with their driver-tree template size and linked company count. Use when the investor wants to review which sectors are tracked.
---

# 業種一覧を閲覧する (List Sectors)

Spec: `domain/usecase/investor/list_sectors/usecase.md`

## 手順

1. 以下を実行する:
   ```
   uv run python scripts/sectors.py list
   ```
2. stdout の JSON 配列（各要素: `id`, `name`, `driverTreeTemplateCount`, `companyCount`, `createdAt`）を、投資家が読みやすい表形式に整形して提示する。
3. 0件の場合は「登録済みの業種はまだありません」と伝え、`register-sector` skill での新規登録を提案する。
4. `driverTreeTemplateCount` が0のSectorがあれば、テンプレート整備が未着手であることを添える。
