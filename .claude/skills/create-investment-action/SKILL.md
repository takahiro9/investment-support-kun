---
name: create-investment-action
description: Record the investor's own action (entry/add/hold/reduce/exit) on a Company — position-sizing rationale, next research priority, and a bear case. Use when the investor is ready to decide what they themselves will do, the system's terminal output.
---

# 投資家自身の打ち手を記録する (Create Investment Action)

Spec: `domain/usecase/investor/create_investment_action/usecase.md`, `domain/usecase/investor/create_investment_action/tech_context.md`

宛先は経営者ではなく投資家自身。`Thesis`/`StrategyRecommendation`/`market` カテゴリの `Signal` を横断して合成される、システムの最終出力。

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. 打ち手（`action`: `entry`/`add`/`hold`/`reduce`/`exit`）を確認する。
3. 判断の根拠にした `Thesis` 群（`relatedThesisIds`）、`StrategyRecommendation` 群（`relatedStrategyRecommendationIds`）を任意で確認する（`list-theses`/`view-strategy-recommendations` で引く）。
4. ポジションサイズの根拠（`positionSizingRationale`、必須）を確認する。確度（対象 Thesis の `probability`）と下値リスク（`invalidation` 発生時の想定損失）の関数であることを文章で説明してもらう。任意で定量化できれば `positionSizePercent` も確認する。
5. 不確実性が最も大きい論点（`nextResearch`、必須。ドライバーツリーの空白ノードの解消タスク等、`view-company` で確認できる）を確認する。
6. 反対側の論証（`bearCase`）を用意する: 集めた Thesis/Signal/Finding をもとに、この打ち手に対する最も強い反論（Red Team の視点）を自分で組み立てて `bearCase` に書く。生成をスキップする場合は空のまま進めてよいが、その場合「Red Team未実施」になることを投資家に伝える。
7. UUID を生成する: `uuidgen`
8. 以下を実行する:
   ```
   uv run python scripts/investment_actions.py create --id <uuid生成結果> --company-id "<companyId>" \
     --action "<action>" --position-sizing-rationale "<positionSizingRationale>" \
     --next-research "<nextResearch>" \
     [--related-thesis-ids "<id1>,<id2>"] [--related-strategy-recommendation-ids "<id1>,<id2>"] \
     [--position-size-percent <数値>] [--bear-case "<bearCase>"] [--body "<任意の本文>"]
   ```
9. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - `positionSizingRationale`/`nextResearch` が空
   - `companyId`/`relatedThesisIds`/`relatedStrategyRecommendationIds` が存在しない
10. 成功時は stdout の JSON をもとに記録完了を伝える。`warnings`（対象 Company に Thesis がない場合の根拠が薄い旨の警告）と `redTeamPending`（`bearCase` が空かどうか）があれば投資家に伝える。

## 注意

`data/vault/investment_actions/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
