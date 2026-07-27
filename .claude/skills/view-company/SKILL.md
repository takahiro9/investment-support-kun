---
name: view-company
description: View a Company's full picture — basic info, current-snapshot summary, driver-tree fill status, and linked Findings. Use when the investor wants to see how well-understood a tracked company is and what's still a blank spot.
---

# 対象企業の詳細を閲覧する (View Company)

Spec: `domain/usecase/investor/view_company/usecase.md`

## 手順

1. 対象 Company の id を確認する。分からなければ `list-companies` skill で引く。
2. 以下を実行する:
   ```
   uv run python scripts/companies.py view --id "<id>"
   ```
3. コマンドが非ゼロで終了した場合（対象 Company が存在しない）、404相当のエラーとして伝える。
4. 成功時は stdout の JSON をもとに提示する:
   - **基本情報**: `ticker`、`name`、`market`、`fiscalYearEnd`、`sectorIds`/`primarySectorId`
   - **現在地スナップショット** (`currentSnapshot`): `asOf` と `summary`。`null` の場合は「まだスナップショットが作成されていません」と伝え、`update-company-snapshot` skill を提案する
   - **ドライバーツリー** (`driverTree`): 各ノードの `filled` を見て、埋まっているノードと空白のノードを可視化する。空白ノードは「次に埋めるべき論点」として強調する。`driverTree` が空なら「ドライバーツリーが未整備です」と伝える
   - **紐づく Finding** (`findings`): 保存日時の新しい順。0件なら「まだ情報が紐づけられていません」と伝え、`add-finding` skill を提案する
   - **Thesis** (`theses`): 現時点では常に空配列（Thesis は Phase 2 未実装のため）。「まだ投資仮説が立てられていません」ではなく、その旨（未実装）を伝える

## 注意

参照のみ。Vault の書き込みは行わない。
