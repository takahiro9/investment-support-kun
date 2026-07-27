---
name: structure-prediction-from-thought
description: Structure a free-form type=prediction Thought into a proper Prediction — horizon, probability, and an observable to resolve against later. Use when a previously-logged prediction is ready to become trackable and resolvable.
---

# 予測を構造化する (Structure Prediction from Thought)

Spec: `domain/usecase/investor/structure_prediction_from_thought/usecase.md`, `domain/usecase/investor/structure_prediction_from_thought/tech_context.md`

## 事前条件

構造化元となる `type=prediction` の `Thought` が存在すること。まだない場合は `add-thought` skill（`type: prediction`）で自由記述の予測を先に書き留めるよう案内する。

## 手順

1. 構造化したい `type=prediction` の `Thought` の id を確認する（`sourceThoughtId`）。分からなければ対象 Company を `view-company` で辿り、紐づく Thought を確認する。
2. 派生元とする `Thesis` の id を確認する（`thesisId`。`list-theses --company-id` で引く）。
3. 元の Thought の自由記述をもとに、予測そのもの（`statement`）、期限（`horizon`、日付）、確度（`probability`、0〜1）を整理してもらう。
4. 何をもって答え合わせするかの人間可読な説明（`observableText`、必須）を確認する。
5. 対象指標が既に `Signal` として記録され始めている場合は、任意で機械判定用の `observableRef` を確認する: `signalMetric`（Signal の `metric` 名と一致させる）、`comparator`（`>`/`>=`/`<`/`<=`/`=`）、`threshold`、任意で `unit`。まだ Signal化されていない場合はこの手順を省略し `observableText` のみで進める。
6. UUID を生成する: `uuidgen`
7. 以下を実行する:
   ```
   uv run python scripts/predictions.py add --id <uuid生成結果> --thesis-id "<thesisId>" \
     --source-thought-id "<sourceThoughtId>" --statement "<statement>" --horizon "<YYYY-MM-DD>" \
     --probability <0-1> --observable-text "<observableText>" \
     [--signal-metric "<metric>" --comparator "<comparator>" --threshold <値> [--observable-unit "<unit>"]] \
     [--body "<予測の背景>"]
   ```
8. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - `statement`/`observableText` が空
   - `thesisId` が存在しない
   - `sourceThoughtId` が存在しない、または `type=prediction` でない
   - `signal-metric`/`comparator`/`threshold` を一部だけ指定した（3つとも指定するか、すべて省略する）
9. 成功時は stdout の JSON をもとに構造化完了を伝える。`resolvedAt`/`outcome`/`postmortem` は未設定のまま保存されることを伝える。

## 注意

`data/vault/predictions/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
