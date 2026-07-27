---
name: view-investment-actions
description: View the history of the investor's own recorded InvestmentActions for a Company — what was decided, why, and the bear case. Use when the investor wants to review past position decisions and their rationale.
---

# 投資家自身の打ち手を閲覧する (View Investment Actions)

Spec: `domain/usecase/investor/view_investment_actions/usecase.md`

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. 以下を実行する:
   ```
   uv run python scripts/investment_actions.py list --company-id "<id>"
   ```
3. stdout の JSON 配列（`createdAt` の新しい順）を、各要素の `action`、`positionSizingRationale`、`positionSizePercent`、`nextResearch`、`bearCase`、根拠にした `Thesis`/`StrategyRecommendation` とあわせて提示する。
4. 0件の場合は「まだ打ち手が記録されていません」と伝え、`create-investment-action` skill を提案する。
5. `redTeamPending` が真の項目（`bearCase` が空）は一覧上で「Red Team未実施」と明示する。

## 注意

参照のみ。Vault の書き込みは行わない。
