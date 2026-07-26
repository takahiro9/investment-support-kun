# 予測一覧を閲覧する (List Predictions)

## 目的・概要

投資家が、記録済みの `Prediction`（個別予測）の一覧と、答え合わせ待ち・的中・外れの内訳を確認する。自身の予測精度（ヒット率）を振り返り、どの種類の予測が得意/不得意かを把握するための画面。

## 事前条件

- なし

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は「予測一覧」へのアクセスをリクエストする。任意で対象 `Company` / `Thesis` や `outcome` による絞り込み条件を指定する。
2. システムは、条件に合致する `Prediction` を取得する。
3. システムは、取得した Prediction を `horizon` の順に並べ、`resolvedAt` が未設定かつ `horizon` を過ぎているものを「答え合わせ待ち」として強調表示する。
4. システムは、`resolvedAt` が設定済みの Prediction について、`outcome` ごとの件数・割合（ヒット率）を集計し、あわせて提示する。

## 代替フロー・例外フロー

- **2a. 記録された Prediction が0件の場合:**
  システムは空のリストを表示し、[Structure Prediction from Thought](../structure_prediction_from_thought/usecase.md) への導線を提示する。
- **3a. 答え合わせ待ちの Prediction がある場合:**
  投資家はこの画面から直接 [Resolve Prediction](../resolve_prediction/usecase.md) へ遷移できる。

## 関連するドメインモデル

- [Prediction](../../../data/prediction.md)
- [Thesis](../../../data/thesis.md)
