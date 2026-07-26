# 予測を構造化する (Structure Prediction from Thought)

## 目的・概要

`Thesis` の `status` 推移だけでは「予測」にならない（時間軸・確度・観測可能な帰結を持たないため）。それまで `type = prediction` の `Thought` として自由記述で書き溜めていた個別の予測を、独立した `Prediction` エンティティへ構造化する。答え合わせ（resolution）を残すこと自体が差別化であり、時間軸・確度・観測方法を明示することで、後から答え合わせできる形にする。

## 事前条件

- 構造化元となる `type = prediction` の `Thought` が存在すること
- その Thought が関係する `Company` に、派生元とする `Thesis` が存在すること

## 事後条件

- 新しい `Prediction` がシステムに保存されること

## 基本フロー（正常系）

1. 投資家は、構造化したい `type = prediction` の `Thought` を選択する（`sourceThoughtId`）。
2. 投資家は、派生元とする `Thesis`（`thesisId`）を選択する。
3. 投資家は、予測そのもの（`statement`）、期限（`horizon`）、確度（`probability`）を、元の Thought の自由記述をもとに整理して入力する。
4. 投資家は、何をもって答え合わせするかの人間可読な説明（`observableText`）を入力する。機械判定可能な場合（対象指標が既に `Signal` として記録され始めている場合）は、任意で `observableRef`（`signalMetric`/`comparator`/`threshold`/`unit`）を設定する。
5. システムは、`statement`/`observableText` が空文字列でないこと、`thesisId` が実在する Thesis を指すことを検証する。
6. システムは、新しい `Prediction` エンティティを作成し、保存する（`resolvedAt`/`outcome`/`postmortem` は未設定のまま）。
7. システムは、構造化完了を投資家に通知する。

## 代替フロー・例外フロー

- **4a. 対象指標がまだ `Signal`化されていない場合:**
  システムは `observableRef` を設定せず、`observableText` のみで保存する。後日その指標が `Signal` として記録され始めた時点で、`observableRef` を追加設定できる。
- **5a. `statement` または `observableText` が空の場合:**
  システムはエラーを返し、入力を促す。
- **1a. まだ `type = prediction` の Thought がない場合:**
  投資家はこの画面から先に [Add Thought](../add_thought/usecase.md) で予測を自由記述として書き留めることができる。

## 関連するドメインモデル

- [Prediction](../../../data/prediction.md)
- [Thought](../../../data/thought.md)
- [Thesis](../../../data/thesis.md)
- [Signal](../../../data/signal.md)
