---
name: view-strategy-recommendations
description: View the generated StrategyRecommendation evaluation table for a Company — execution probability, impact, and priced-in level side by side. Use when the investor wants to compare management-strategy options before deciding their own InvestmentAction.
---

# 経営の打ち手の評価を閲覧する (View Strategy Recommendations)

Spec: `domain/usecase/investor/view_strategy_recommendations/usecase.md`

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. 以下を実行する:
   ```
   uv run python scripts/strategy_recommendations.py list --company-id "<id>"
   ```
3. stdout の JSON 配列（各要素: `option`, `executionEvidence`, `executionProbability`, `impactIfExecuted`, `pricedIn`, `relatedThesisIds`, `createdAt`）を評価テーブルとして提示する。投資家の関心に応じて `pricedIn` が低い順や `impactIfExecuted` の大きい順など並び替えて見せる。
4. 0件の場合は「まだ評価が行われていません」と伝え、`generate-strategy-recommendation` skill を提案する。

## 注意

参照のみ。Vault の書き込みは行わない。
