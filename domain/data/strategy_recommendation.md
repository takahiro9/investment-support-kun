# StrategyRecommendation — 経営の打ち手の評価

## 概要

Thesis・Signal・業界/政策/社会動向のFindingを踏まえ、**「経営の打ち手の選択肢 × 実行確率 × 業績インパクト」の評価テーブル**を出力する中間生成物。「A社はこうすべき」という規範的な提案ではなく、「A社がこの打ち手を取る確率と、取った場合のインパクト」を評価する（宛先はあくまで投資家自身であり、経営への提案ではない）。

最終的な投資家自身の打ち手は[InvestmentAction](investment_action.md)が担う。StrategyRecommendationはその入力となる中間生成物。

市場の織り込み度（`pricedIn`）は持たない。これは純粋に投資家自身の判断材料であり、経営の打ち手そのものの評価（実行確率・インパクト）には不要なため。市場の織り込みを踏まえた投資判断が必要な場合は、関連する[Thesis](thesis.md)の`consensusView`/`variant`/`whyMispriced`（`status=established`到達時に必須）を参照する。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `companyId` | string (FK) | ✅ | 対象Company |
| `relatedThesisIds` | string[] (FK) | ❌ | 評価の根拠にしたThesis群 |
| `option` | string | ✅ | 打ち手の選択肢（例: "サブスク転換"） |
| `executionEvidence` | string | ✅ | 実行確率の根拠（過去の資本配分実績・経営陣のインセンティブ設計・実行ケイパビリティ等） |
| `executionProbability` | `ExecutionProbability` | ✅ | 実行確率（定性区分） |
| `impactIfExecuted` | string | ✅ | 実行された場合の業績インパクト（例: "利益+X%"） |
| `createdAt` | datetime | ✅ | 作成日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `ExecutionProbability`

| 値 | 説明 |
|---|---|
| `low` | 実行確率は低い |
| `medium` | 実行確率は中程度 |
| `high` | 実行確率は高い |

---

## 不変条件・ビジネスルール

- `companyId` は必須
- `option`/`executionEvidence`/`impactIfExecuted` は空文字列にできない
- 「A社はこうすべき」という規範的な提案文にせず、選択肢・根拠・確率・インパクトの評価という形を崩さない

---

## 他ドメインオブジェクトとの関係

- **Company** — StrategyRecommendationは1つのCompanyについての評価（多対1）
- **[Thesis](thesis.md)** — 評価の根拠として複数のThesisを参照してよい（多対多、任意）
- **[InvestmentAction](investment_action.md)** — InvestmentActionの入力として参照される

---

## 保存フォーマット（大方針）

StrategyRecommendationは `data/vault/strategy_recommendations/<id>.md` に YAML フロントマターとして保存する。本文（任意）には評価の詳しい論証を書いてよい。
