# 対象企業を登録する (Register Company)

## 目的・概要

投資家が、投資判断の中心単位となる `Company`（対象企業）を新規登録する。登録時に、企業のヘッドライン分類（`primarySectorId`）が指す `Sector` のドライバーツリーテンプレートをコピーし、その企業専用の事業構造分解木（`driverTree`）の初期状態を作る。以降、投資家はこのドライバーツリーの各ノードを [Finding](../../../data/finding.md) と [Thought](../../../data/thought.md) を通じて埋めていくことになる。

## 事前条件

- `primarySectorId` として指定する `Sector` が存在すること

## 事後条件

- 新しい `Company` がシステムに保存されること
- `driverTree` が、`primarySectorId` の指す `Sector` の `driverTreeTemplate` をコピーした状態で初期化されていること（テンプレートが空の場合は空のまま）

## 基本フロー（正常系）

1. 投資家は、証券コード（`ticker`）、市場区分（`market`）、企業名（`name`）、決算期（`fiscalYearEnd`）、実質的な事業を持つ業種群（`sectorIds`、1つ以上）、およびそのうちヘッドライン分類とする1つ（`primarySectorId`）を入力し、登録をリクエストする。
2. システムは、`ticker` が空文字列でなく、システム全体で一意であることを検証する。
3. システムは、`sectorIds` が1つ以上であり、`primarySectorId` が `sectorIds` に含まれることを検証する。
4. システムは、`primarySectorId` が指す `Sector` の `driverTreeTemplate` を取得し、これをコピーして `driverTree` の初期値とする。
5. システムは、新しい `Company` エンティティを作成し、保存する。
6. システムは、登録完了を投資家に通知し、登録された Company の詳細画面（[View Company](../view_company/usecase.md)）へ遷移させる。

## 代替フロー・例外フロー

- **2a. `ticker` が未入力、または既に登録済みの場合:**
  システムはエラーメッセージを返し、処理を中断する。
- **3a. `sectorIds` が空、または `primarySectorId` が `sectorIds` に含まれない場合:**
  システムはエラーメッセージを返し、入力を促す。
- **1a. 対象企業の事業に対応する `Sector` がまだ存在しない場合:**
  投資家はこの画面から新しい Sector を作成するフロー（[Register Sector](../register_sector/usecase.md)）へ遷移できる。
- **4a. `primarySectorId` の指す `Sector` の `driverTreeTemplate` が空の場合:**
  システムは `driverTree` を空配列のまま Company を作成する。ドライバーツリーは登録後、個社の実情に応じて個別に組み立ててよい。

## 関連するドメインモデル

- [Company](../../../data/company.md)
- [Sector](../../../data/sector.md)
