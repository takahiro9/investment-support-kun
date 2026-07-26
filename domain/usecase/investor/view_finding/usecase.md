# Finding の詳細を閲覧する (View Finding)

## 目的・概要

自動収集されたり、手動で追加された単一の `Finding`（情報アイテム）の詳細内容と出所区分（`evidenceTier`）を確認する。また、その Finding に付与されている `Thought`（意味づけ）も合わせて表示する。企業発信の情報が確証バイアスの温床にならないよう、出所区分は常に本文とセットで目立つ位置に示す。

## 事前条件

- 対象となる `Finding` が存在すること

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、Finding 一覧等から特定の `Finding` を選択する。
2. システムは、指定された `Finding` の詳細情報（タイトル、URL、種別、`evidenceTier`、本文等）を取得する。
3. システムは、その Finding を `findingIds` に含む `Thought` の一覧を取得する。
4. システムは、Finding のメタデータ（`evidenceTier` を先頭に目立つ形で表示）と本文、および紐づく Thought の一覧（それぞれが指す Company / Sector / Theme、ドライバーツリーのノードを含む）をあわせて投資家に提示する。

## 代替フロー・例外フロー

- **2a. 該当する Finding が存在しない場合:**
  システムは 404 Not Found エラーを表示する。
- **3a. 紐づく Thought が0件の場合:**
  システムは「まだ意味づけが行われていません」というメッセージと、Thought を追加するための導線（[Add Thought](../add_thought/usecase.md)）を提示する。
- **4a. Finding の種別が `web_article` / `disclosure` で本文（`body`）を持たない場合:**
  システムはタイトルとURLを表示し、元コンテンツへ遷移するためのリンクボタンを強調表示する。

## 関連するドメインモデル

- [Finding](../../../data/finding.md)
- [Thought](../../../data/thought.md)
