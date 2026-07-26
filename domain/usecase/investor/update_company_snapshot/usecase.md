# 現在地スナップショットを更新する (Update Company Snapshot)

## 目的・概要

`Finding` / `Thought` が数十〜数百件溜まった `Company` について、毎回全件読み直さずに「今どういう状況か」を把握できるよう、`currentSnapshot`（日付つきの要約）を書き直す。Finding / Thought の蓄積を踏まえた、定期的な棚卸し作業。

## 事前条件

- 対象となる `Company` が存在すること

## 事後条件

- 対象 `Company` の `currentSnapshot`（`asOf` と `summary`）が更新されること
- 対象 `Company` の `updatedAt` が更新されること

## 基本フロー（正常系）

1. 投資家は、[View Company](../view_company/usecase.md) 等の画面から、対象 `Company` のスナップショット更新をリクエストする。
2. システムは、前回の `currentSnapshot.asOf` 以降に追加された `Finding` / `Thought`（その Company に紐づくもの）を取得する。
3. システムは、取得した Finding / Thought をもとに要約の草案を生成し、投資家に提示する。
4. 投資家は、提示された草案を確認・編集し、最終的な要約文（`summary`）を確定する。
5. システムは、`asOf` を現在日時、`summary` を確定した要約として `currentSnapshot` を更新し、`updatedAt` を現在日時に更新して保存する。
6. システムは、更新完了を投資家に通知する。

## 代替フロー・例外フロー

- **2a. 前回更新以降、新しい Finding / Thought が存在しない場合:**
  システムはその旨を伝えたうえで、投資家が更新を続行するか中止するかを選択できるようにする。
- **3a. 要約草案の自動生成に失敗した場合、または対象 Finding / Thought が0件の場合:**
  システムは草案の提示を省略し、投資家に `summary` の手入力を求める。
- **4a. 投資家が更新を取りやめた場合:**
  システムは `currentSnapshot` を変更せずに処理を終了する。

## 関連するドメインモデル

- [Company](../../../data/company.md)
- [Finding](../../../data/finding.md)
- [Thought](../../../data/thought.md)
