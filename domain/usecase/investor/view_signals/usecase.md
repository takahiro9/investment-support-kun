# 時系列指標を閲覧する (View Signals)

## 目的・概要

投資家が、特定の `Thesis` の前提を検証している `Signal`（時系列指標）の推移を確認する。前提が想定どおり進んでいるか、`invalidation` / `confirmation` の兆候が数値として現れているかを判断するための画面。

## 事前条件

- なし

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、[View Thesis](../view_thesis/usecase.md) 等の画面から、対象 `Thesis` に紐づく Signal 一覧の表示をリクエストする。任意で `category` による絞り込みを指定する。
2. システムは、`validatesThesisId` が対象 Thesis を指す `Signal` をすべて取得する。
3. システムは、取得した Signal を `metric` ごとにグルーピングし、`period` の時系列順に並べて投資家に提示する。各 Signal には `validatesAssumption`（何を検証しているか）と `extractionMethod`（取得方法）をあわせて表示する。

## 代替フロー・例外フロー

- **2a. 紐づく Signal が0件の場合:**
  システムは「まだ指標が記録されていません」というメッセージと、[Record Signal Manually](../record_signal_manually/usecase.md) への導線を提示する。
- **3a. 同一 `metric`/`period` の組み合わせで複数の Signal（改訂履歴）が存在する場合:**
  システムはそれらを時系列の1点としてではなく、改訂の推移として並べて表示する。

## 関連するドメインモデル

- [Signal](../../../data/signal.md)
- [Thesis](../../../data/thesis.md)
