---
name: record-signal
description: Manually record a time-series Signal (financial/operational/leading metric) that validates a specific Thesis assumption. Use when the investor read a number in a disclosure/IR doc and wants to track it against a hypothesis.
---

# 時系列指標を手動で記録する (Record Signal Manually)

Spec: `domain/usecase/investor/record_signal_manually/usecase.md`, `domain/usecase/investor/record_signal_manually/tech_context.md`

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. この指標が前提を検証する対象の `Thesis`（`validatesThesisId`）を確認する。まだ Thesis がなければ `create-thesis` skill を先に案内する（分からなければ `list-theses --company-id` で引く）。
3. 指標の分類（`category`: `financial`/`operational`/`leading`）、指標名（`metric`）、対象期間・時点（`period`、例: `2027Q2`）、値（`value`）、任意で単位（`unit`）を確認する。
4. この指標が Thesis のどの前提を検証するものかを一言で確認する（`validatesAssumption`、省略不可）。
5. 任意でこの数値の抽出元となった `Finding` の id を確認する（`sourceFindingId`）。
6. UUID を生成する: `uuidgen`
7. 以下を実行する:
   ```
   uv run python scripts/signals.py record --id <uuid生成結果> --company-id "<companyId>" \
     --category "<category>" --metric "<metric>" --period "<period>" --value <value> \
     --validates-thesis-id "<thesisId>" --validates-assumption "<validatesAssumption>" \
     [--unit "<unit>"] [--source-finding-id "<findingId>"]
   ```
8. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - `validatesAssumption` が空(「何のために見ているか分からない時系列データ置き場にしない」ため必須)
   - `companyId`/`validatesThesisId`/`sourceFindingId` が存在しない
   - `validatesThesisId` が指す Thesis が `companyId` と異なる Company に属している
9. 成功時は stdout の JSON をもとに記録完了を伝える。同一 `companyId`/`metric`/`period` の組み合わせが既にあっても上書きせず、履歴として積み上がることを伝える。

## 注意

`data/vault/signals/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
