---
name: generate-strategy-recommendation
description: Evaluate the management strategy options available to a Company — execution probability and expected impact — as an input to the investor's own InvestmentAction. Use when the investor wants a structured read on what management might do next, not a "you should do X" recommendation.
---

# 経営の打ち手を評価する (Generate Strategy Recommendation)

Spec: `domain/usecase/investor/generate_strategy_recommendation/usecase.md`, `domain/usecase/investor/generate_strategy_recommendation/tech_context.md`

宛先は経営者ではなく投資家自身であることを常に意識する。出力は「A社はこうすべき」という規範的な提案文にせず、**打ち手の選択肢 × 実行確率 × 業績インパクト** の評価テーブルという形式を崩さない。市場の織り込み度は扱わない（経営の打ち手評価そのものには不要なため）。

## 事前条件

対象 `Company` に少なくとも1つの `Thesis` が存在すること。存在しない場合は評価を実行せず、`create-thesis` skill を案内する（`list-theses --company-id` で確認できる）。

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. 対象 Company の `Thesis` 群（`view-thesis`/`list-theses`）、`Signal`（`view-signals`）、および Sector/Theme レイヤーの Finding/Thought（`view-company`、`list-themes`）を収集し読み込む。
3. 収集した情報をもとに、経営が取りうる打ち手の選択肢（`option`）を複数洗い出す。洗い出せる選択肢が0件なら「現時点で評価に足る材料が揃っていません」と伝え、追加で必要な Finding/Thought の種類を提示して終了する。
4. 選択肢ごとに以下を評価する:
   - `executionEvidence`/`executionProbability`（実行確率とその根拠。過去の資本配分実績・経営陣のインセンティブ設計・実行ケイパビリティ等から）
   - `impactIfExecuted`（実行された場合の業績インパクト）
   - 根拠にした `Thesis`（`relatedThesisIds`）
5. UUID を生成する: `uuidgen`（選択肢ごとに1つ）
6. 選択肢ごとに以下を実行する（1回の評価リクエストにつき選択肢の数だけ実行する）:
   ```
   uv run python scripts/strategy_recommendations.py add --id <uuid生成結果> --company-id "<companyId>" \
     --option "<option>" --execution-evidence "<executionEvidence>" \
     --execution-probability "<low|medium|high>" --impact-if-executed "<impactIfExecuted>" \
     [--related-thesis-ids "<id1>,<id2>"] [--body "<詳しい論証>"]
   ```
7. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - `option`/`executionEvidence`/`impactIfExecuted` が空
   - 対象 Company に Thesis が1件もない
   - `relatedThesisIds` に存在しない Thesis が含まれる
8. 全選択肢の登録が完了したら、生成された評価テーブルを投資家に提示する（`view-strategy-recommendations` 相当の一覧表示）。

## 注意

`data/vault/strategy_recommendations/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
