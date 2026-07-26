# Company — 対象企業

## 概要

投資判断の中心単位。ticker・市場区分・セクター・決算期などのIDを持つマスタエンティティ。1つのCompanyに対し、複数のSource（IR、業界ニュース、市場データ等）・複数のThesisが紐づく。

### 1つのCompanyは複数のSectorに属してよい

銘柄としての市場区分（`market`）は単一だが、事業の実態は複数のSectorにまたがることが珍しくない（例: 味の素は食品企業として分類されるが、ABF（半導体パッケージング材料）事業も持つ）。市場がこの複数事業性を見落として単一セクターの企業として評価している場合、それ自体が[Thesis](thesis.md)の`whyMispriced`の材料になりうる。そのため`sectorId`は単一FKにせず、`sectorIds`（複数可）+ `primarySectorId`（既定のヘッドライン分類）の形で持つ。

- `sectorIds` — このCompanyが実質的な事業を持つSectorすべて（パイロットの「同一セクター内3〜5社」やSector別の銘柄一覧は、いずれかの`sectorIds`に一致するCompanyを対象にする）
- `primarySectorId` — 市場が主にどのセクターの企業として評価しているか（`sectorIds`のいずれか1つ）。ドライバーツリーの初期テンプレートのコピー元として使う

ドライバーツリーの各セグメント（ルート直下のノード）がどのSectorの事業かを`DriverTreeNode.sectorId`で個別に紐づけられるようにし、「食品セグメントは食品Sector、電子材料セグメントは半導体材料Sector」のように事業構造レベルで複数セクター性を表現する。

### ドライバーツリー（事業構造の骨格）

Findingを溜めるだけでは「理解が深まったか」を測れない。Companyは以下のような分解木（`driverTree`）を持ち、各ノードを[Thought](thought.md)を介して埋めていく。

```
売上 = セグメントA（数量 × 単価）+ セグメントB（顧客数 × ARPU × 継続率）
利益 = 売上 − 原価（主要コストドライバー）− 販管費
競争ポジション = シェア / 参入障壁 / 代替脅威 / 顧客集中度
```

具体的な分解軸はSector（業種）によって大きく異なるため、単一の固定テンプレートは持たない。Company作成時に`primarySectorId`の指すSectorの`driverTreeTemplate`をコピーして初期化し、以後は個社の実情に応じて個別化していく（セクター増加を見据え、業種ごとに分解構造が異なることを前提にする）。埋まっているノードと空白のノードが可視化されることで「解像度」が初めて測定可能になる。空白ノード＝次に埋めに行くべき論点であり、受動的なSource巡回から能動的な調査への転換点になる。

**ノードとFindingの関連付けはThoughtが担う**。「意味づけはすべてThoughtが担う」という原則により、Company自身やFindingはドライバーツリーのノードへの参照を持たない。あるFindingがどのノードの埋め合わせになるかは、そのFindingに対するThoughtの`driverNodeIds`が表す（詳細は[Thought](thought.md)を参照）。

### 現在地スナップショット（as-of更新サマリ）

Findingが数十〜数百件溜まった状態で「今どういう状況か」を毎回全件読み直すのは非現実的。Companyは日付つきの要約フィールド（`currentSnapshot`）を持ち、Finding追加時に差分更新する。

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
| `driverTree` | `DriverTreeNode[]` | ❌ | 事業構造の分解木。Sectorのテンプレートをコピーして個別化したもの。空配列で始めてもよい |
| `currentSnapshot` | `CompanySnapshot` | ❌ | 現在地の要約（as-of日付つき）。初回スナップショット作成前はnull |
| `createdAt` | datetime | ✅ | 登録日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `DriverTreeNode`

事業構造の分解木を構成する1ノード。SectorのテンプレートとCompanyの個別化されたツリーの両方で同じ構造を使う。

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✅ | ツリー内で一意のノードID（例: `revenue.segmentA.volume`） |
| `label` | string | ✅ | ノードのラベル（例: "セグメントA 数量"） |
| `parentId` | string \| null | ❌ | 親ノードのid。ルートノードは`null` |
| `formula` | string | ❌ | このノードが子ノードからどう計算されるかの説明（例: "数量 × 単価"）。葉ノードは空でよい |
| `sectorId` | string (FK) | ❌ | このノード（主にルート直下のセグメントノードを想定）がどのSectorの事業かを表す。単一セクターの企業では省略してよく、`primarySectorId`が暗黙の値になる。事業セグメントが複数Sectorにまたがる企業（例: 食品セグメント＝食品Sector、電子材料セグメント＝半導体材料Sector）でのみ明示する |

木構造はフラットな配列 + `parentId` で表現する（ネスト構造にはしない。ノードの追加・移動が配列操作だけで完結するため）。

### `CompanySnapshot`

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `asOf` | date | ✅ | このサマリが反映している時点 |
| `summary` | string | ✅ | 現在地の要約本文 |

---

## 不変条件・ビジネスルール

- `ticker` はシステム全体で一意
- `sectorIds` は1つ以上。各要素は[Sector](sector.md)のidを指す（実在チェックは行わない。参照先が見つからない場合は表示時に`missing`として顕在化する）。要素の重複は持たない
- `primarySectorId` は必須で、`sectorIds` に含まれる要素のいずれかでなければならない
- Company作成時、`driverTree` は指定がなければ `primarySectorId` の指す Sector の `driverTreeTemplate` をコピーして初期化する（テンプレートが空ならCompanyの`driverTree`も空で始まる）
- `driverTree` の各ノードの `id` はCompany内で一意。`parentId` は同一Company内の別ノードの`id`を指す（存在しない`parentId`は不可。ルートは`null`）
- `DriverTreeNode.sectorId` を指定する場合、`sectorIds` に含まれる要素でなければならない
- `currentSnapshot` はシステムが自動計算するものではなく、Finding/Thought蓄積を踏まえて都度書き直す運用上のフィールド（v1では自動生成ロジックを持たない）

---

## 他ドメインオブジェクトとの関係

- **Sector** — Companyは1つ以上のSectorに属してよい（多対多）。`primarySectorId`がヘッドライン分類、`sectorIds`が実質的な事業を持つSectorすべてを表す
- **Source** — 企業レイヤー・市場レイヤーのSourceはCompanyに紐づく（`companyId`を持つ）
- **Thought** — CompanyへのFindingの意味づけは、Thoughtの`companyIds`（および`driverNodeIds`）を介して行う。Company自身はFindingへの参照を持たない
- **[Thesis](thesis.md)** — Thesisは必ずひとつのCompanyについての仮説である（多対1、`Thesis.companyId`）。1つのCompanyは複数のThesisを持ってよい
- **[Signal](signal.md)** — Companyの時系列指標（`Signal.companyId`）
- **[StrategyRecommendation](strategy_recommendation.md) / [InvestmentAction](investment_action.md)** — いずれもCompanyに紐づく

---

## 保存フォーマット（大方針）

Companyは `data/vault/companies/<id>.md` に YAML フロントマター（属性一覧のメタデータ、`driverTree`はYAMLのリストで持つ）＋ Markdown本文（任意）の形で保存する。本文には企業概要・事業内容など、構造化しにくい背景説明を書いてよい。
