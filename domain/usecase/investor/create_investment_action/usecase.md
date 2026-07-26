# 投資家自身の打ち手を記録する (Create Investment Action)

## 目的・概要

投資家が、「どのような打ち手が取れそうか」という問いに直接答える `InvestmentAction` を記録する。宛先は経営者ではなく投資家自身であり、`Thesis` / `StrategyRecommendation` / `market` カテゴリの `Signal` を横断して合成される、システムの最終出力（終端レイヤー）となる。

確証バイアス対策として、Red Teamエージェント（反対側の論証を作る役割）による `bearCase` の作成とあわせて運用する。

## 事前条件

- 対象となる `Company` が存在すること

## 事後条件

- 新しい `InvestmentAction` がシステムに保存されること

## 基本フロー（正常系）

1. 投資家は、対象の `Company` を選択し、打ち手（`action`: `entry` / `add` / `hold` / `reduce` / `exit`）を選択する。
2. 投資家は、判断の根拠にした `Thesis` 群（`relatedThesisIds`）、`StrategyRecommendation` 群（`relatedStrategyRecommendationIds`）を任意で選択する。
3. 投資家は、ポジションサイズの根拠（`positionSizingRationale`）を記述する。根拠は確度（対象 Thesis の `probability`）と下値リスク（`invalidation` 発生時の想定損失）の関数であることを文章で説明する。任意で定量化できる場合は `positionSizePercent` を入力する。
4. 投資家は、不確実性が最も大きい論点（`nextResearch`。ドライバーツリーの空白ノードの解消タスク等）を記述する。
5. システムは、Red Teamエージェントに反対側の論証（`bearCase`）の作成を依頼する。
6. システムは、`positionSizingRationale`/`nextResearch` が空文字列でないことを検証する。
7. システムは、新しい `InvestmentAction` エンティティを作成し、保存する。
8. システムは、記録完了を投資家に通知する。

## 代替フロー・例外フロー

- **5a. `bearCase` の生成に失敗した場合、または投資家が生成をスキップした場合:**
  システムは `bearCase` を空のまま保存できるが、Red Team導入後の運用ではこの `InvestmentAction` は完了条件を満たさないものとして一覧上で明示する（[InvestmentAction の不変条件](../../../data/investment_action.md#不変条件ビジネスルール)）。
- **6a. `positionSizingRationale` または `nextResearch` が空の場合:**
  システムはエラーを返し、入力を促す。
- **1a. 対象 Company にまだ `Thesis` が存在しない場合:**
  投資家は打ち手の記録自体は行えるが、システムは根拠が薄い旨を警告として表示する。

## 関連するドメインモデル

- [InvestmentAction](../../../data/investment_action.md)
- [Thesis](../../../data/thesis.md)
- [StrategyRecommendation](../../../data/strategy_recommendation.md)
- [Company](../../../data/company.md)
