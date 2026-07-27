---
name: view-signals
description: View the time-series Signals validating a specific Thesis's assumptions, grouped by metric and ordered by period. Use when the investor wants to check whether a hypothesis's premises are tracking as expected.
---

# 時系列指標を閲覧する (View Signals)

Spec: `domain/usecase/investor/view_signals/usecase.md`

## 手順

1. 対象 Thesis の id を確認する（分からなければ `list-theses`/`view-thesis` skill）。任意で `category` による絞り込みを確認する。
2. 以下を実行する:
   ```
   uv run python scripts/signals.py list --thesis-id "<id>" [--category "<category>"]
   ```
3. stdout の JSON 配列を `metric` ごとにグルーピングし、`period` の時系列順に並べて提示する。各 Signal には `validatesAssumption`（何を検証しているか）と `extractionMethod`（取得方法）をあわせて表示する。
4. 0件の場合は「まだ指標が記録されていません」と伝え、`record-signal` skill を提案する。
5. 同一 `metric`/`period` の組み合わせで複数件ある場合は、改訂履歴として時系列に並べて表示する（上書きではない）。

## 注意

参照のみ。Vault の書き込みは行わない。
