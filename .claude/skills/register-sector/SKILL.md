---
name: register-sector
description: Register a new Sector (業種) in the investment vault. Use when the investor wants to add a new industry/sector classification, optionally with a driver-tree template.
---

# 業種を登録する (Register Sector)

Spec: `domain/usecase/investor/register_sector/usecase.md`, `domain/usecase/investor/register_sector/tech_context.md`

## 手順

1. 投資家に業種名（`name`、必須）を確認する。ドライバーツリーテンプレート（`driverTreeTemplate`）は任意 — 未入力なら空のまま登録してよい。テンプレートを入れる場合、各ノードは `{id, label, parentId, formula}` の形（`domain/data/company.md#drivertreenode` 参照）。
2. UUID を生成する: `uuidgen`
3. 以下を実行する:
   ```
   uv run python scripts/sectors.py register --id <uuid生成結果> --name "<name>" \
     [--driver-tree-template '<JSON配列>'] [--body "<任意の本文>"]
   ```
4. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を投資家に分かりやすく伝え、再入力を促す。よくある失敗:
   - `name` が空
   - 同名の Sector が既に登録済み（「この業種は既に登録されています」と伝える）
5. 成功時は stdout の JSON（登録された Sector の内容）をもとに、登録完了を投資家に伝える。

## 注意

- `data/vault/sectors/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
