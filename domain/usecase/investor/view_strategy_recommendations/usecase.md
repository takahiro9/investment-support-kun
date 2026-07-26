# 経営の打ち手の評価を閲覧する (View Strategy Recommendations)

## 目的・概要

投資家が、対象 `Company` について生成済みの `StrategyRecommendation`（経営の打ち手の評価）一覧を確認する。実行確率・業績インパクト・市場の織り込み度を並べて見比べ、投資家自身の打ち手（[InvestmentAction](../create_investment_action/usecase.md)）を検討するための画面。

## 事前条件

- 対象となる `Company` が存在すること

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、対象 `Company` の詳細画面等から「経営の打ち手の評価」一覧の表示をリクエストする。
2. システムは、`companyId` が対象 Company を指す `StrategyRecommendation` をすべて取得する。
3. システムは、`pricedIn`（市場の織り込み度）が低い順、あるいは `impactIfExecuted` が大きい順など、投資家の関心に沿った並び替えを可能にしつつ、選択肢ごとの評価テーブルを提示する。

## 代替フロー・例外フロー

- **2a. 評価が1件も存在しない場合:**
  システムは「まだ評価が行われていません」というメッセージと、[Generate Strategy Recommendation](../generate_strategy_recommendation/usecase.md) への導線を提示する。

## 関連するドメインモデル

- [StrategyRecommendation](../../../data/strategy_recommendation.md)
- [Company](../../../data/company.md)
