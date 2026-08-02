# 事業仮説の詳細を閲覧する (View Thesis)

## 目的・概要

特定の `Thesis`（事業仮説）について、その論証内容・反証/確証条件・現在のライフサイクル状態、および根拠となった `Thought` 群を確認する。仮説の妥当性を見直し、次に何を検証すべきかを判断するための画面。

## 事前条件

- 対象となる `Thesis` が存在すること

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、Company 詳細画面や Thesis 一覧から特定の `Thesis` を選択する。
2. システムは、指定された `Thesis` の詳細情報（`statement`、`invalidation`/`confirmation`、`horizon`/`probability`、`status`、論証本文）を取得する。
3. システムは、`thoughtIds` が指す `Thought` 群を取得し、それぞれが根ざす `Finding` とあわせて提示する。
4. システムは、この Thesis を `validatesThesisId` に持つ `Signal` の一覧、および `thesisId` に持つ `Prediction` の一覧が存在すれば、あわせて取得する。
5. システムは、以上の情報を投資家に提示する。`status` は目立つ位置に、`invalidation`/`confirmation` は対で表示する。

## 代替フロー・例外フロー

- **2a. 該当する Thesis が存在しない場合:**
  システムは 404 Not Found 相当のエラーを表示する。
- **4a. 紐づく Signal / Prediction が存在しない場合:**
  システムはその欄を省略、または「まだありません」と表示する。
- **status が `challenged` の場合:**
  システムは警告表示とともに、[Update Thesis Status](../update_thesis_status/usecase.md) への導線を強調する。

## 関連するドメインモデル

- [Thesis](../../../data/thesis.md)
- [Thought](../../../data/thought.md)
- [Company](../../../data/company.md)
