# 経営の打ち手を評価する (Generate Strategy Recommendation)

## 目的・概要

投資家が、対象 `Company` について「経営が取りうる打ち手の選択肢」を評価する `StrategyRecommendation` の生成をシステムに依頼する。宛先は経営者ではなく投資家自身であり、出力は「A社はこうすべき」という規範的な提案ではなく、**打ち手の選択肢 × 実行確率 × 業績インパクト** の評価テーブルである。市場の織り込み度は扱わない（経営の打ち手そのものの評価には不要なため）。この評価は、投資家自身の打ち手（[InvestmentAction](../../../data/investment_action.md)）を組み立てるための中間生成物として使う。

## 事前条件

- 対象となる `Company` が存在すること
- 対象 `Company` に少なくとも1つの `Thesis` が存在すること（Thesisを踏まえない評価は根拠が薄いため）

## 事後条件

- 新しい `StrategyRecommendation` が1件以上システムに保存されること（打ち手の選択肢ごとに1件）

## 基本フロー（正常系）

1. 投資家は、対象の `Company` を選択し、経営の打ち手の評価をリクエストする。
2. システムは、対象 Company の `Thesis` 群、`Signal`（`financial`/`operational`/`leading` 各カテゴリ）、および業界・政策・社会動向を扱う `Sector`/`Theme` レイヤーの `Finding`/`Thought` を収集する。
3. システムは、収集した情報をもとに、経営が取りうる打ち手の選択肢（`option`）を複数洗い出す。
4. システムは、選択肢ごとに以下を評価する:
   - `executionEvidence` / `executionProbability`（実行確率とその根拠。過去の資本配分実績・経営陣のインセンティブ設計・実行ケイパビリティ等から）
   - `impactIfExecuted`（実行された場合の業績インパクト）
5. システムは、評価した選択肢それぞれを `StrategyRecommendation` エンティティとして保存する。根拠にした Thesis 群があれば `relatedThesisIds` に記録する。
6. システムは、生成された評価テーブルを投資家に提示する。

## 代替フロー・例外フロー

- **2a. 対象 Company に Thesis が存在しない場合:**
  システムは評価を実行せず、[Create Thesis](../create_thesis/usecase.md) への導線を提示する。
- **3a. 洗い出せる選択肢が0件の場合:**
  システムは「現時点で評価に足る材料が揃っていません」と表示し、追加で必要な Finding / Thought の種類を提示する。

## 関連するドメインモデル

- [StrategyRecommendation](../../../data/strategy_recommendation.md)
- [Thesis](../../../data/thesis.md)
- [Signal](../../../data/signal.md)
- [Company](../../../data/company.md)
