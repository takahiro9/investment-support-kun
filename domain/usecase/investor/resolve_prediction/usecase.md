# 予測の答え合わせをする (Resolve Prediction)

## 目的・概要

投資家が、期限（`horizon`）を迎えた、あるいは判定材料が揃った `Prediction` について、的中したか外れたかを記録する。既存の投資リサーチAIも、人間のアナリストの多くも自分の予測精度を記録していないなかで、答え合わせを残すこと自体が仕組みとしての差別化になる。「解釈の質」という主観的な概念を、ヒット率・キャリブレーションという測定可能な指標に変換する起点となる。

## 事前条件

- 対象となる `Prediction` が存在し、`resolvedAt` が未設定であること

## 事後条件

- 対象 `Prediction` の `resolvedAt`/`outcome` が設定されること
- `outcome` が `miss` または `ambiguous` の場合、`postmortem` が設定されること

## 基本フロー（正常系）

1. 投資家は、答え合わせ待ちの `Prediction` 一覧から対象を選択する。
2. システムは、`observableRef` が設定されている場合、対応する `Signal`（同一 Company の同名 `metric` を持ち、`period` が `horizon` に対応するもの）を検索し、判定結果の候補を提示する。
3. 投資家は、判定結果候補を確認のうえ、最終的な結果（`outcome`: `hit` / `miss` / `ambiguous`）を確定する。
4. `outcome` が `miss` または `ambiguous` の場合、投資家は前提のどこが間違っていたかを `postmortem` に記述する。
5. システムは、`resolvedAt` を現在日時、`outcome`（と該当する場合は `postmortem`）を設定して保存する。
6. システムは、答え合わせ完了を投資家に通知する。

## 代替フロー・例外フロー

- **2a. `observableRef` が未設定、または対応する `Signal` が見つからない場合:**
  システムは判定結果候補を提示せず、投資家に `observableText` を手がかりとした手動判定を求める。
- **4a. `outcome = hit` の場合:**
  `postmortem` は任意（成功要因を書き残したい場合のみ記述する）。
- **1a. `horizon` を過ぎても答え合わせが行われていない `Prediction` がある場合:**
  システムはこれを「答え合わせ待ち」として一覧上で強調する（[Prediction の不変条件](../../../data/prediction.md#不変条件ビジネスルール)）。

## 関連するドメインモデル

- [Prediction](../../../data/prediction.md)
- [Signal](../../../data/signal.md)
