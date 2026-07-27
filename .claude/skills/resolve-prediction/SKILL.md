---
name: resolve-prediction
description: Record whether a Prediction hit, missed, or was ambiguous once its horizon has passed, with a postmortem on misses. Use when a forecast's deadline has arrived and it's time to score it.
---

# 予測の答え合わせをする (Resolve Prediction)

Spec: `domain/usecase/investor/resolve_prediction/usecase.md`, `domain/usecase/investor/resolve_prediction/tech_context.md`

## 事前条件

対象 `Prediction` が存在し、まだ答え合わせ（`resolvedAt`）が行われていないこと。

## 手順

1. 対象 Prediction の id を確認する（分からなければ `list-predictions` skill、とくに `awaitingResolution` の項目から）。
2. 判定材料を集める:
   ```
   uv run python scripts/predictions.py resolution-context --id "<id>"
   ```
   `observableRef` が設定されていれば、対応する `Signal` から算出した判定候補（`candidates`: `suggestedOutcome` 付き）が返る。設定されていない、または候補が見つからない場合は `candidates` が空になるので、`prediction.observableText` を手がかりに投資家自身の手動判定を求める。
3. 投資家に判定候補を提示し、最終的な結果（`outcome`: `hit`/`miss`/`ambiguous`）を確定してもらう。
4. `outcome` が `miss` または `ambiguous` の場合、前提のどこが間違っていたかを `postmortem` に記述してもらう（必須）。`hit` の場合は任意。
5. 以下を実行する:
   ```
   uv run python scripts/predictions.py resolve --id "<id>" --outcome "<outcome>" [--postmortem "<postmortem>"]
   ```
6. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - 対象 Prediction が既に答え合わせ済み
   - `outcome` が `miss`/`ambiguous` なのに `postmortem` が空
7. 成功時は stdout の JSON（更新後の Prediction）をもとに答え合わせ完了を伝える。

## 注意

本ユースケースは `resolvedAt`/`outcome`/`postmortem` のみを更新する部分更新であり、他のフィールドは変更しない。`data/vault/predictions/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
