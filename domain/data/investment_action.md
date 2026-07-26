# InvestmentAction — 投資家自身の打ち手

## 概要

目的「どのような打ち手が取れそうか」に直接答える、システムの終端レイヤー。宛先は経営者ではなくユーザー自身。Thesis・StrategyRecommendation・market Signalを横断して合成される、システムの最終出力。

Phase 4で導入し、以降Red Teamエージェント（bear case生成）とあわせて運用する。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `companyId` | string (FK) | ✅ | 対象Company |
| `relatedThesisIds` | string[] (FK) | ❌ | 判断の根拠にしたThesis群 |
| `relatedStrategyRecommendationIds` | string[] (FK) | ❌ | 判断の根拠にしたStrategyRecommendation群 |
| `action` | `InvestmentActionType` | ✅ | 打ち手 |
| `positionSizingRationale` | string | ✅ | ポジションサイズの根拠（確度[Thesis.probability]と下値リスク[invalidation発生時の想定損失]の関数であることを文章で説明） |
| `positionSizePercent` | number | ❌ | ポジションサイズの目安（ポートフォリオに対する比率、%）。定量化できる場合のみ |
| `nextResearch` | string | ✅ | 不確実性が最も大きい論点（ドライバーツリーの空白ノードの解消タスク等） |
| `bearCase` | string | ❌ | Red Teamエージェントが作成する反対側の論証 |
| `createdAt` | datetime | ✅ | 作成日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `InvestmentActionType`

| 値 | 説明 |
|---|---|
| `entry` | エントリー（新規建て） |
| `add` | 積み増し |
| `hold` | 保有継続 |
| `reduce` | 縮小 |
| `exit` | 撤退 |

---

## 不変条件・ビジネスルール

- `companyId` は必須
- `positionSizingRationale`/`nextResearch` は空文字列にできない
- `bearCase` が空のInvestmentActionは、Red Team導入後の運用では完了条件を満たさない（確証バイアス対策として反対側の論証を伴わせる）

---

## 他ドメインオブジェクトとの関係

- **Company** — InvestmentActionは1つのCompanyについての打ち手（多対1）
- **[Thesis](thesis.md) / [StrategyRecommendation](strategy_recommendation.md)** — 判断の根拠として参照する（多対多、任意）

---

## 保存フォーマット（大方針）

InvestmentActionは `data/vault/investment_actions/<id>.md` に YAML フロントマターとして保存する。本文（任意）には判断の詳しい論証を書いてよい。
