# 投資仮説一覧を閲覧する (List Theses)

## 目的・概要

投資家が、特定の `Company` に紐づく、あるいはシステム全体の `Thesis`（投資仮説）一覧を確認する。どの仮説が育っており、どれが要レビュー（`challenged`）状態かを俯瞰し、優先して検証すべき仮説を選ぶための画面。

## 事前条件

- なし

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は「投資仮説一覧」へのアクセスをリクエストする。任意で対象 `Company` や `status` による絞り込み条件を指定する。
2. システムは、条件に合致する `Thesis` を取得する（デフォルトは `status` が `dropped` 以外のもの）。
3. システムは、取得した Thesis の一覧（`statement`、対象 Company、`status`、`updatedAt`）を、`status` ごとにグルーピングするなどして投資家に提示する。

## 代替フロー・例外フロー

- **2a. 該当する Thesis が0件の場合:**
  システムは空のリストを表示し、[Create Thesis](../create_thesis/usecase.md) への導線を提示する。
- **2b. `status = dropped` の Thesis も見たい場合:**
  投資家がフィルタ条件を変更することで、棄却済みの Thesis も一覧に含めて表示できる（過去に検討し外した仮説を再確認する用途）。
- **3a. `status = challenged` の Thesis が存在する場合:**
  システムはこれを一覧上で強調表示し、優先的なレビューを促す。

## 関連するドメインモデル

- [Thesis](../../../data/thesis.md)
- [Company](../../../data/company.md)
