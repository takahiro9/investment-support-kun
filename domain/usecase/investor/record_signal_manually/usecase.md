# 時系列指標を手動で記録する (Record Signal Manually)

## 目的・概要

投資家が、決算資料や適時開示などを読んで気づいた数値（売上高、稼働率、求人数、株価等）を、`Thesis` の前提を検証するための時系列データポイント（`Signal`）として記録する。Signal は単体では意味を持たず、「この指標は Thesis のどの前提を検証するためのものか」を明示して初めて記録できる。

## 事前条件

- 対象となる `Company` が存在すること
- 検証対象となる `Thesis`（`validatesThesisId`）が存在し、対象 `Company` に属すること

## 事後条件

- 新しい `Signal` がシステムに保存されること

## 基本フロー（正常系）

1. 投資家は、対象の `Company` と、この指標が前提を検証する対象の `Thesis`（`validatesThesisId`）を選択する。
2. 投資家は、指標の分類（`category`: `financial` / `operational` / `leading` / `market`）、指標名（`metric`）、対象期間・時点（`period`）、値（`value`）、単位（`unit`）を入力する。
3. 投資家は、この指標が Thesis のどの前提を検証するものかを一言で説明する（`validatesAssumption`）。
4. 投資家は、任意でこの数値の抽出元となった `Finding` を選択する（`sourceFindingId`）。
5. システムは、`companyId`/`validatesThesisId`/`validatesAssumption` が空でないこと、`validatesThesisId` が指す Thesis が `companyId` と同じ Company に属することを検証する。
6. システムは、新しい `Signal` エンティティを `extractionMethod = manual` として作成し、保存する。
7. システムは、記録完了を投資家に通知する。

## 代替フロー・例外フロー

- **1a. 対象 Thesis がまだ存在しない場合:**
  投資家はこの画面から新しい Thesis を作成するフロー（[Create Thesis](../create_thesis/usecase.md)）へ遷移できる。
- **3a. `validatesAssumption` が未入力の場合:**
  システムはエラーを返し、入力を促す（「何のために見ているか分からない時系列データ置き場にしない」という設計方針のため、この項目は省略できない）。
- **同一 `companyId`/`metric`/`period` の組み合わせで既に Signal が存在する場合:**
  システムは上書きせず、履歴として新しい Signal を追加保存する（改訂・再取得の履歴を積み上げるため）。

## 関連するドメインモデル

- [Signal](../../../data/signal.md)
- [Thesis](../../../data/thesis.md)
- [Company](../../../data/company.md)
- [Finding](../../../data/finding.md)
