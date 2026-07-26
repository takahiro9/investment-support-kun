# 投資仮説のステータスを遷移させる (Update Thesis Status)

## 目的・概要

投資家が、証拠（`Thought`）の蓄積や `invalidation` / `confirmation` 条件への抵触を踏まえ、`Thesis` の認識論的ライフサイクル（`status`）を遷移させる。Thesis は作成して終わりではなく、`seed` → `developing` → `established` と育つか、あるいは `challenged` を経て `dropped` に至るかを、投資家自身が判断し続ける必要がある。

## 事前条件

- 対象となる `Thesis` が存在すること

## 事後条件

- 対象 `Thesis` の `status` が更新されること
- 対象 `Thesis` の `updatedAt` が更新されること

## 基本フロー（正常系）

1. 投資家は、[View Thesis](../view_thesis/usecase.md) 等の画面から、対象 `Thesis` のステータス変更をリクエストする。
2. システムは、現在の `status` と、選択可能な遷移先を提示する。
3. 投資家は、遷移先の `status` を選択する。`developing` → `established` への遷移、および `challenged` への遷移の場合は、その判断理由を任意で本文に追記できる。
4. システムは、`status` を更新し、`updatedAt` を現在日時に更新して保存する。
5. システムは、更新完了を投資家に通知する。

## 代替フロー・例外フロー

- **3a. `invalidation` 条件に抵触する事実が新たに判明した場合:**
  投資家はまず `status` を `challenged` に遷移させる。この時点では `dropped` へは進めず、一時的なノイズか本質的な崩れかを見極めたうえで、改めて `dropped` または元の `status` への復帰を判断する（[Thesis の不変条件](../../../data/thesis.md#不変条件ビジネスルール)）。
- **3b. `established` への遷移を試みるが `consensusView`/`variant`/`whyMispriced` が実用的な粒度で書けていない場合:**
  システムは遷移前にこれらのフィールドの見直しを促す（Thesis作成時点で必須項目として埋まっているため、通常は内容の粒度が論点になる）。
- **3c. `dropped` への遷移の場合:**
  システムは確認を求める（以降この Thesis は一覧のデフォルト表示から外れるため）。

## 関連するドメインモデル

- [Thesis](../../../data/thesis.md)
