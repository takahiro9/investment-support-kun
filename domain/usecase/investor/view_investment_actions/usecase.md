# 投資家自身の打ち手を閲覧する (View Investment Actions)

## 目的・概要

投資家が、対象 `Company` について記録済みの `InvestmentAction`（投資家自身の打ち手）の履歴を確認する。過去にどの時点でどう判断し、その根拠は何だったか、反対側の論証（`bearCase`）はどうだったかを振り返るための画面。

## 事前条件

- 対象となる `Company` が存在すること

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、対象 `Company` の詳細画面等から「打ち手の履歴」の表示をリクエストする。
2. システムは、`companyId` が対象 Company を指す `InvestmentAction` を、`createdAt` の新しい順に取得する。
3. システムは、各 InvestmentAction の情報（`action`、`positionSizingRationale`、`positionSizePercent`、`nextResearch`、`bearCase`、根拠にした Thesis / StrategyRecommendation）を一覧として投資家に提示する。

## 代替フロー・例外フロー

- **2a. 記録された InvestmentAction が0件の場合:**
  システムは「まだ打ち手が記録されていません」というメッセージと、[Create Investment Action](../create_investment_action/usecase.md) への導線を提示する。
- **3a. `bearCase` が空の InvestmentAction がある場合:**
  システムは一覧上で「Red Team未実施」であることを明示する。

## 関連するドメインモデル

- [InvestmentAction](../../../data/investment_action.md)
- [Company](../../../data/company.md)
