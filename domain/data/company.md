# Company — 対象企業

## 概要

投資判断の中心単位。ticker・市場区分・セクター・決算期などのIDを持つマスタエンティティ。1つのCompanyに対し、複数のSource（IR、業界ニュース、市場データ等）・複数の[Business](business.md)（個別事業単位）・複数のThesisが紐づく。

事業構造の分解木（driverTree）と事業単位の現在地スナップショットは[Business](business.md)が持つ。Companyは「銘柄としてのマスタ情報」に専念し、「実際にどんな事業から構成されているか」はBusinessに委ねる（詳細は[Business](business.md)を参照）。

### 1つのCompanyは複数のSectorに属してよい

銘柄としての市場区分（`market`）は単一だが、事業の実態は複数のSectorにまたがることが珍しくない（例: 味の素は食品企業として分類されるが、ABF（半導体パッケージング材料）事業も持つ）。市場がこの複数事業性を見落として単一セクターの企業として評価している場合、それ自体が[Thesis](thesis.md)の`whyMispriced`の材料になりうる。そのため`sectorId`は単一FKにせず、`sectorIds`（複数可）+ `primarySectorId`（既定のヘッドライン分類）の形で持つ。

- `sectorIds` — このCompanyが実質的な事業を持つSectorすべて（パイロットの「同一セクター内3〜5社」やSector別の銘柄一覧は、いずれかの`sectorIds`に一致するCompanyを対象にする）。配下の各[Business](business.md)の`sectorId`は、必ずこの`sectorIds`に含まれる
- `primarySectorId` — 市場が主にどのセクターの企業として評価しているか（`sectorIds`のいずれか1つ）。あくまで「市場からの見え方」であり、実際にどの事業が中核かを表す[Business](business.md)`.isPrimary`とは独立している（両者のズレ自体が`whyMispriced`の材料になりうる）

かつては複数事業性をCompany直下の`driverTree`のノード単位`sectorId`で表現していたが、事業自体を[Business](business.md)という第一級エンティティに切り出したことで、「食品事業は食品Sector、ABF事業は半導体材料Sector」のようにBusinessごとの`sectorId`で素直に表現できるようになった。

### 現在地スナップショット（会社全体・複数事業にまたがる状況のas-of更新サマリ）

Companyは日付つきの要約フィールド（`currentSnapshot`）を持つ。ただしこれは個別事業の状況ではなく、資本政策・株式分割・配当方針・M&A・全社連結決算に含まれる一過性損益など、特定の[Business](business.md)に一意に属さない会社全体の状況を対象とする。個別事業の状況は各Businessの`currentSnapshot`が担う。したがって、ある会社の全体像を把握するには「Companyのスナップショット」＋「配下の全Businessのスナップショット」を合わせて見る必要がある。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `ticker` | string | ✅ | 証券コード |
| `market` | string | ✅ | 市場区分（例: "東証プライム"） |
| `sectorIds` | string[] (FK) | ✅ | 実質的な事業を持つ [Sector](sector.md) 群（1つ以上） |
| `primarySectorId` | string (FK) | ✅ | ヘッドライン分類として使うSector。`sectorIds`のいずれか1つ |
| `name` | string | ✅ | 企業名 |
| `fiscalYearEnd` | string | ✅ | 決算期（例: "03-31"、月日のみ保持） |
| `currentSnapshot` | `CompanySnapshot` | ❌ | 会社全体（複数事業にまたがる話題）の現在地の要約（as-of日付つき）。初回スナップショット作成前はnull |
| `createdAt` | datetime | ✅ | 登録日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `CompanySnapshot`

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `asOf` | date | ✅ | このサマリが反映している時点 |
| `summary` | string | ✅ | 会社全体の現在地の要約本文 |

---

## 不変条件・ビジネスルール

- `ticker` はシステム全体で一意
- `sectorIds` は1つ以上。各要素は[Sector](sector.md)のidを指す（実在チェックは行わない。参照先が見つからない場合は表示時に`missing`として顕在化する）。要素の重複は持たない
- `primarySectorId` は必須で、`sectorIds` に含まれる要素のいずれかでなければならない
- Company作成時、少なくとも1つの[Business](business.md)（`isPrimary=true`）が同時に作成される（Companyは単独では存在せず、常に1つ以上のBusinessを伴う）
- `currentSnapshot` はシステムが自動計算するものではなく、Finding/Thought蓄積を踏まえて都度書き直す運用上のフィールド（v1では自動生成ロジックを持たない）

---

## 他ドメインオブジェクトとの関係

- **Sector** — Companyは1つ以上のSectorに属してよい（多対多）。`primarySectorId`がヘッドライン分類、`sectorIds`が実質的な事業を持つSectorすべてを表す
- **[Business](business.md)** — 1つのCompanyは1つ以上のBusinessを持つ（多対1、`Business.companyId`）。事業構造の分解木と事業単位のスナップショットはBusiness側が持つ
- **Source** — 企業レイヤー・市場レイヤーのSourceはCompanyに紐づく（`companyId`を持つ）
- **Thought** — CompanyへのFindingの意味づけは、Thoughtの`companyIds`を介して行う。ドライバーツリーのノードへの紐付けは`businessIds`/`driverNodeIds`が担う（詳細は[Thought](thought.md)を参照）
- **[Thesis](thesis.md)** — Thesisは必ずひとつのCompanyについての仮説である（多対1、`Thesis.companyId`）。任意で特定のBusinessにも紐づく（`Thesis.businessId`）。1つのCompanyは複数のThesisを持ってよい
- **[Signal](signal.md)** — Companyの時系列指標（`Signal.companyId`）
- **[StrategyRecommendation](strategy_recommendation.md) / [InvestmentAction](investment_action.md)** — いずれもCompanyに紐づく

---

## 保存フォーマット（大方針）

Companyは `data/vault/companies/<id>.md` に YAML フロントマター（属性一覧のメタデータ）＋ Markdown本文（任意）の形で保存する。本文には企業概要など、構造化しにくい背景説明を書いてよい。
