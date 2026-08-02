---
name: update-thesis-status
description: Transition a Thesis's lifecycle status (seed -> developing -> established, or -> challenged -> dropped) as evidence accumulates or invalidation conditions are hit. Use when the investor wants to advance, flag, or retire a hypothesis.
---

# 事業仮説のステータスを遷移させる (Update Thesis Status)

Spec: `domain/usecase/investor/update_thesis_status/usecase.md`, `domain/usecase/investor/update_thesis_status/tech_context.md`

## 手順

1. 対象 Thesis の id を確認する（分からなければ `list-theses`/`view-thesis` skill）。
2. 現在の `status` を確認し、遷移先を投資家に選んでもらう: `seed` / `developing` / `established` / `challenged` / `dropped`
   - `invalidation` 条件に抵触する事実が判明した場合は、まず `challenged` への遷移を勧める（`dropped` へは進めない）
3. 任意で遷移理由の本文追記（`note`）をもらう。
4. 以下を実行する:
   ```
   uv run python scripts/theses.py update-status --id "<id>" --status "<新status>" [--note "<理由>"]
   ```
5. 終了コードで分岐する:
   - **exit 1**（`{"errors": [...]}`）: 対象 Thesis が存在しない。
   - **exit 2**（`{"warning": "...", "requiresConfirm": true}`）: `dropped` への遷移は確認が必要という警告。内容を投資家に伝え、確定するなら同じコマンドに `--confirm` を付けて再実行する。
   - **exit 0**: 成功。stdout の JSON（更新後の Thesis）をもとに完了を伝える。

## 注意

- 本ユースケースは `status`/`updatedAt`（および任意の本文追記）のみを更新する部分更新であり、他のフィールドは変更しない。
- `data/vault/theses/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
