---
name: view-finding
description: View a single Finding's detail — evidenceTier, content, and every Thought that gives it meaning. Use when the investor wants to inspect one information item and see how it's been interpreted.
---

# Finding の詳細を閲覧する (View Finding)

Spec: `domain/usecase/investor/view_finding/usecase.md`

## 手順

1. 対象 Finding の id を確認する。分からない場合は次のコマンドで検索を手伝う:
   ```
   uv run python scripts/findings.py list [--type "<type>"] [--evidence-tier "<tier>"]
   ```
   タイトルや URL から目視で対象を絞り込む。
2. 以下を実行する:
   ```
   uv run python scripts/findings.py view --id "<id>"
   ```
3. コマンドが非ゼロで終了した場合（stderr `{"errors": [...]}`、対象 Finding が存在しない）、404相当のエラーとして伝える。
4. 成功時は stdout の JSON（`finding`: メタデータ+本文、`thoughts`: 紐づく Thought の配列）をもとに提示する:
   - `evidenceTier` を本文より先頭・目立つ位置に表示する（企業発信の情報が無自覚に中立な事実として扱われないため）
   - `finding.body` を本文として表示する。`url`/`disclosure`系で本文が空なら、タイトルと URL を強調し元コンテンツへのリンクを示す
   - 紐づく `thoughts` を一覧表示する（各 Thought の `type`、本文、`companyIds`/`sectorIds`/`themeIds`、`driverNodeIds`）
5. `thoughts` が0件の場合は「まだ意味づけが行われていません」と伝え、`add-thought` skill での追加を提案する。

## 注意

参照のみ。Vault の書き込みは行わない。
