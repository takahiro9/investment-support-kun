---
name: list-theses
description: List investment Theses, optionally filtered by Company or status, grouped so 'challenged' ones stand out. Use when the investor wants to see which hypotheses are maturing and which need review.
---

# 投資仮説一覧を閲覧する (List Theses)

Spec: `domain/usecase/investor/list_theses/usecase.md`

## 手順

1. 投資家に絞り込み条件が必要か確認する（任意）: 対象 `Company`（id が分からなければ `list-companies` skill）、`status`（`seed`/`developing`/`established`/`challenged`/`dropped`）。
2. 以下を実行する:
   ```
   uv run python scripts/theses.py list [--company-id "<id>"] [--status "<status>"]
   ```
   `--status` を指定しない場合、デフォルトで `dropped` は結果から除外される。棄却済みも見たい場合は `--status dropped` を明示する。
3. stdout の JSON 配列（各要素: `id`, `companyId`, `statement`, `status`, `updatedAt` 等）を `status` ごとにグルーピングするなどして提示する。
4. `status = challenged` の Thesis があれば一覧上で強調し、`update-thesis-status` skill での見直しを促す。
5. 0件の場合は「登録済みの投資仮説はまだありません」と伝え、`create-thesis` skill での新規作成を提案する。

## 注意

参照のみ。Vault の書き込みは行わない。
