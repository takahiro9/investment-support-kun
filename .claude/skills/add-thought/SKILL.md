---
name: add-thought
description: Add a Thought (Findingへの意味づけ) linking one or more Findings to a Company/Sector/Theme and, optionally, a driver-tree node. Use whenever a Finding needs interpretation — what it means, what it relates to, and what it fills in.
---

# Thought を追加する (Add Thought)

Spec: `domain/usecase/investor/add_thought/usecase.md`, `domain/usecase/investor/add_thought/tech_context.md`

## 手順

1. 起点となる1つ以上の `Finding` の id を確認する。分からない場合は `uv run python scripts/findings.py list` で検索を手伝う。
2. `type` を確認する:
   - `note`: 気づき・観察・主張
   - `question`: 探求したい問い・引っかかり
   - `prediction`: 時間軸・確度つきの予測を自由記述で（「何が・いつまでに・何%くらいで起きると思うか」を本文に書く。Phase 5 で Prediction として構造化されるまでのログ）
3. 本文（`body`）に考察を書いてもらう（必須、空不可）。
4. 任意でこの Thought が関係する `companyIds` / `sectorIds` / `themeIds` を確認する（id が分からなければ `list-companies`/`list-sectors`/`list-themes` skill で引く）。
5. 対象 Company のドライバーツリーの特定ノードを埋めるものであれば、そのノード id（`driverNodeIds`）も確認する。ノード一覧は `view-company` skill（`uv run python scripts/companies.py view --id <companyId>`）の `driverTree` から拾える。`driverNodeIds` を指定する場合は必ず対応する `companyIds` も指定する。
6. UUID を生成する: `uuidgen`
7. 以下を実行する:
   ```
   uv run python scripts/thoughts.py add --id <uuid生成結果> \
     --finding-ids "<id1>,<id2>" --type "<type>" --body "<本文>" \
     [--company-ids "<id1>,..."] [--sector-ids "<id1>,..."] [--theme-ids "<id1>,..."] \
     [--driver-node-ids "<nodeId1>,..."] [--tags "tag1,tag2"]
   ```
8. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝え、再入力を促す。よくある失敗:
   - `findingIds` が空、または存在しない Finding を指している
   - `body` が空
   - `driverNodeIds` を指定したのに `companyIds` が空、またはそのノードが指定した Company の `driverTree` に存在しない
   - 指定した `companyIds`/`sectorIds`/`themeIds` が存在しない
9. 成功時は stdout の JSON をもとに登録完了を伝える。`driverNodeIds` を指定した場合は、対象 Company のドライバーツリーの該当ノードが埋まったことも一言添える。

## 注意

- `data/vault/thoughts/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
- Company/Sector/Theme ↔ Finding の関連付けはこの Thought を介してのみ成立する（Finding/Company 自身は直接の関連を持たない）。
