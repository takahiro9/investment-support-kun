# 対象企業の詳細を閲覧する (View Company)

## 目的・概要

特定の `Company`（対象企業）について、その基本情報・現在地スナップショット・ドライバーツリーの充足状況・紐づく `Finding` / `Thought` / `Thesis` を確認する。「この企業の理解はどこまで進み、何が空白として残っているか」を一望するための、投資家にとってのメイン画面となる。

## 事前条件

- 対象となる `Company` が存在すること

## 事後条件

- なし（参照のみ）

## 基本フロー（正常系）

1. 投資家は、一覧画面などから特定の `Company` を選択する。
2. システムは、指定された `Company` の詳細情報（証券コード、企業名、市場区分、決算期、`sectorIds`/`primarySectorId`、`currentSnapshot`）を取得する。
3. システムは、`driverTree` の各ノードについて、[Thought](../../../data/thought.md) の `driverNodeIds` を辿って紐づく Finding の有無を判定し、埋まっているノードと空白のノードを可視化する。
4. システムは、その Company の `companyIds` に含む `Thought` を辿って、紐づく `Finding` の一覧を取得する（保存日時の新しい順などでソート）。
5. システムは、その Company を `companyId` に持つ `Thesis` の一覧（`statement` と `status`）を取得する。
6. システムは、以上の情報を投資家に提示する。空白ノードは「次に埋めるべき論点」として強調表示する。

## 代替フロー・例外フロー

- **2a. 該当する Company が存在しない場合:**
  システムは 404 Not Found 相当のエラーを表示する。
- **3a. `driverTree` が空の場合:**
  システムは「ドライバーツリーが未整備です」というメッセージを表示する。
- **4a. 紐づく Finding が0件の場合:**
  システムは「まだ情報が紐づけられていません」というメッセージと、情報を手動追加（[Add Finding Manually](../add_finding_manually/usecase.md)）するための導線を提示する。
- **5a. 紐づく Thesis が0件の場合:**
  システムは「まだ投資仮説が立てられていません」というメッセージと、Thesis を作成するフローへの導線を提示する。

## 関連するドメインモデル

- [Company](../../../data/company.md)
- [Finding](../../../data/finding.md)
- [Thought](../../../data/thought.md)
- [Thesis](../../../data/thesis.md)
