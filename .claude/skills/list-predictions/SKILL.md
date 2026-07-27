---
name: list-predictions
description: List recorded Predictions with hit/miss/ambiguous/unresolved breakdown, highlighting ones past their horizon awaiting resolution. Use when the investor wants to review their forecasting track record.
---

# 予測一覧を閲覧する (List Predictions)

Spec: `domain/usecase/investor/list_predictions/usecase.md`

## 手順

1. 投資家に絞り込み条件が必要か確認する（任意）: 対象 `Company`、`Thesis`、`outcome`（`hit`/`miss`/`ambiguous`/`unresolved`）。
2. 以下を実行する:
   ```
   uv run python scripts/predictions.py list [--company-id "<id>"] [--thesis-id "<id>"] [--outcome "<outcome>"]
   ```
3. stdout の JSON（`predictions`: `horizon` 順の配列、`stats`: `outcome` ごとの件数）をもとに提示する。
4. `awaitingResolution` が真の Prediction（`resolvedAt` 未設定かつ `horizon` を過ぎている）を「答え合わせ待ち」として強調し、`resolve-prediction` skill への導線を示す。
5. `stats`（`hit`/`miss`/`ambiguous`/`unresolved` の件数・ヒット率）をあわせて提示する。
6. 0件の場合は「記録された予測はまだありません」と伝え、`structure-prediction-from-thought` skill を提案する。

## 注意

参照のみ。Vault の書き込みは行わない。
