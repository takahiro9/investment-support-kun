---
name: view-thesis
description: View a Thesis's full detail — consensus/variant/mispricing case, invalidation/confirmation conditions, lifecycle status, its source Thoughts/Findings, and any linked Signals/Predictions. Use when the investor wants to reassess a hypothesis.
---

# 投資仮説の詳細を閲覧する (View Thesis)

Spec: `domain/usecase/investor/view_thesis/usecase.md`

## 手順

1. 対象 Thesis の id を確認する。分からなければ `list-theses` skill で引く。
2. 以下を実行する:
   ```
   uv run python scripts/theses.py view --id "<id>"
   ```
3. コマンドが非ゼロで終了した場合（対象 Thesis が存在しない）、404相当のエラーとして伝える。
4. 成功時は stdout の JSON をもとに提示する:
   - `statement`、`consensusView`/`variant`/`whyMispriced`、`invalidation`/`confirmation`（対で表示）、`horizon`/`probability`、論証本文
   - `status` を目立つ位置に表示する。`challenged` の場合は警告とともに `update-thesis-status` skill への導線を強調する
   - `thoughts`: 根拠となった Thought 群とそれぞれが根ざす Finding
   - `signals`: この Thesis の前提を検証している Signal 一覧（0件なら省略可、`record-signal` skill を案内してもよい）
   - `predictions`: この Thesis から派生した Prediction 一覧（0件なら省略可、`structure-prediction-from-thought` skill を案内してもよい）

## 注意

参照のみ。Vault の書き込みは行わない。
