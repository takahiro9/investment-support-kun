# 対象企業一覧を閲覧する (List Companies)

## 目的・概要

投資家が、登録済みの `Company`（対象企業）の一覧を確認する。業種で絞り込み、同一 Sector 内の企業を横並びで比較する起点となる画面。

## 事前条件

- なし

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は「対象企業一覧」へのアクセスをリクエストする。任意で `Sector` による絞り込み条件を指定する。
2. システムは、登録済みの `Company` を取得する（絞り込み条件があれば `sectorIds` に指定 Sector を含むもののみ）。
3. システムは、各 Company の情報（証券コード、企業名、市場区分、ヘッドライン分類となる Sector、`currentSnapshot` の要約と`asOf`）を一覧として投資家に提示する。

## 代替フロー・例外フロー

- **2a. 登録されている Company が0件の場合:**
  システムは空のリストを表示し、新しい Company を登録する（[Register Company](../register_company/usecase.md)）ための導線を提示する。
- **3a. `currentSnapshot` が未作成の Company がある場合:**
  システムは一覧上で「未更新」であることを示す。

## 関連するドメインモデル

- [Company](../../../data/company.md)
- [Sector](../../../data/sector.md)
