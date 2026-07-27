---
name: list-themes
description: List registered Themes with the Sectors they affect and how many Findings are linked to each. Use when the investor wants to review which cross-Sector trends are being tracked.
---

# テーマ一覧を閲覧する (List Themes)

Spec: `domain/usecase/investor/list_themes/usecase.md`

## 手順

1. 以下を実行する:
   ```
   uv run python scripts/themes.py list
   ```
2. stdout の JSON 配列（各要素: `id`, `name`, `description`, `sectorIds`, `findingCount`, `createdAt`）を、投資家が読みやすい表形式に整形して提示する。
3. 0件の場合は「登録済みのテーマはまだありません」と伝え、`create-theme` skill での新規作成を提案する。

## 注意

参照のみ。Vault の書き込みは行わない。`findingCount` はこの Theme を `themeIds` に含む Thought が参照する Finding の延べ件数（重複除去済み）。
