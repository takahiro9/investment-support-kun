---
name: create-theme
description: Register a Theme — a cross-Sector industry/policy/macro trend that isn't confined to a single Sector. Use when a piece of news or policy could affect multiple Sectors/Companies at once.
---

# テーマを作成する (Create Theme)

Spec: `domain/usecase/investor/create_theme/usecase.md`, `domain/usecase/investor/create_theme/tech_context.md`

## 手順

1. テーマ名（`name`、必須）を確認する。
2. 任意で補足説明（`description`）と、このテーマが影響する `Sector` 群（`sectorIds`）を確認する。特定の Sector に限定されないより広いマクロ動向であれば `sectorIds` は空のままでよい。id が分からなければ `list-sectors` skill で引く。
3. UUID を生成する: `uuidgen`
4. 以下を実行する:
   ```
   uv run python scripts/themes.py register --id <uuid生成結果> --name "<name>" \
     [--description "<description>"] [--sector-ids "<id1>,<id2>"] [--body "<任意の本文>"]
   ```
5. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - `name` が空
   - `sectorIds` に重複、または存在しない Sector が含まれる
6. 成功時は stdout の JSON をもとに登録完了を伝える。

## 注意

`data/vault/themes/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
