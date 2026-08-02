# Business — 事業

## 概要

[Company](company.md)（対象企業）の内部に存在する個別の事業単位。1つのCompanyは1つ以上のBusinessを持つ。ドライバーツリーと現在地スナップショットはBusiness単位で持ち、事業ごとの理解の解像度と状況を独立して追跡できるようにする。

Companyが持つのは ticker・市場区分・決算期のような「銘柄としてのマスタ情報」であり、Businessが持つのは「その銘柄の中身が実際にどんな事業から構成されているか」という実態である。1つのCompanyが複数のSectorにまたがる事業を持つケース（例: 味の素は食品企業として分類されるが、ABF（半導体パッケージング材料）事業も持つ）は、事業ごとに独立したBusinessレコードとして表現し、それぞれに実態の`sectorId`を持たせる。

### なぜCompanyから切り出すか

当初はCompanyが単一の`driverTree`（フラット配列 + `parentId`）を持ち、ルート直下のセグメントノードに`sectorId`を個別付与することで複数事業性を表現していた。しかし、[Thesis](thesis.md)や[Signal](signal.md)を「この会社について」ではなく「この会社のこの事業について」の単位で持ちたいという要求が出てきたため、事業自体を他エンティティからFKで参照できる第一級のエンティティとして切り出した。これにより:

- 事業ごとに独立した`driverTree`・`currentSnapshot`を持てる（ある事業は解像度が高いが別の事業はまだ空白、という状態を個別に可視化できる）
- `Thesis`/`Signal`を会社単位・事業単位のどちらでも紐づけられるようになる（詳細は各ドキュメントを参照）
- ノード単位で`sectorId`を分岐させるという回避策が不要になる（Business自体が`sectorId`を持つため、ツリーの全ノードは暗黙にそのSectorに属する）

### ドライバーツリー（事業構造の骨格）

Findingを溜めるだけでは「理解が深まったか」を測れない。Businessは以下のような分解木（`driverTree`）を持ち、各ノードを[Thought](thought.md)を介して埋めていく。

```
売上 = 数量 × 単価
利益 = 売上 − 原価（主要コストドライバー）− 販管費
競争ポジション = シェア / 参入障壁 / 代替脅威 / 顧客集中度
```

具体的な分解軸はSector（業種）によって大きく異なるため、単一の固定テンプレートは持たない。Business作成時に`sectorId`の指すSectorの`driverTreeTemplate`をコピーして初期化し、以後は個社・個別事業の実情に応じて個別化していく。埋まっているノードと空白のノードが可視化されることで「解像度」が初めて測定可能になる。空白ノード＝次に埋めに行くべき論点であり、受動的なSource巡回から能動的な調査への転換点になる。

**ノードとFindingの関連付けはThoughtが担う**。「意味づけはすべてThoughtが担う」という原則により、Business自身やFindingはドライバーツリーのノードへの参照を持たない。あるFindingがどのノードの埋め合わせになるかは、そのFindingに対するThoughtの`driverNodeIds`が表す（詳細は[Thought](thought.md)を参照）。

### 現在地スナップショット（as-of更新サマリ、事業単位）

Findingが数十〜数百件溜まった状態で「この事業は今どういう状況か」を毎回全件読み直すのは非現実的。Businessは日付つきの要約フィールド（`currentSnapshot`）を持ち、Finding追加時に差分更新する。

会社全体・複数事業にまたがる話題（資本政策、株式分割、全社連結決算に含まれる一過性損益、M&A等）はどの事業にも一意に属さないため、Businessの`currentSnapshot`の対象外とし、引き続き[Company](company.md)の`currentSnapshot`が扱う。したがって、ある会社の全体像を把握するには「Companyのスナップショット」＋「配下の全Businessのスナップショット」を合わせて見る必要がある。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `companyId` | string (FK) | ✅ | 親となる [Company](company.md) |
| `sectorId` | string (FK) | ✅ | この事業が実質的に属する [Sector](sector.md)（単一） |
| `name` | string | ✅ | 事業名（例: "スパークプラグ・センサー事業"、"ABF事業"） |
| `isPrimary` | boolean | ✅ | そのCompanyの中核事業かどうか |
| `driverTree` | `DriverTreeNode[]` | ❌ | 事業構造の分解木。Sectorのテンプレートをコピーして個別化したもの。空配列で始めてもよい |
| `currentSnapshot` | `BusinessSnapshot` | ❌ | 事業単位の現在地の要約（as-of日付つき）。初回スナップショット作成前はnull |
| `createdAt` | datetime | ✅ | 登録日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `DriverTreeNode`

事業構造の分解木を構成する1ノード。SectorのテンプレートとBusinessの個別化されたツリーの両方で同じ構造を使う。

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✅ | ツリー内で一意のノードID（例: `revenue.volume`） |
| `label` | string | ✅ | ノードのラベル（例: "販売数量"） |
| `parentId` | string \| null | ❌ | 親ノードのid。ルートノードは`null` |
| `formula` | string | ❌ | このノードが子ノードからどう計算されるかの説明（例: "数量 × 単価"）。葉ノードは空でよい |

木構造はフラットな配列 + `parentId` で表現する（ネスト構造にはしない。ノードの追加・移動が配列操作だけで完結するため）。1つのBusinessは単一のSectorにしか属さないため、旧`Company.DriverTreeNode`が持っていたノード単位の`sectorId`は不要になった。

### `BusinessSnapshot`

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `asOf` | date | ✅ | このサマリが反映している時点 |
| `summary` | string | ✅ | 事業の現在地の要約本文 |

---

## 不変条件・ビジネスルール

- 1つの[Company](company.md)は1つ以上のBusinessを持つ（Companyの登録と同時に、少なくとも1つのBusinessが`isPrimary=true`で作成される）
- 同一`companyId`配下のBusiness群のうち、`isPrimary=true`はちょうど1つ
- `sectorId`は、親Companyの`sectorIds`に含まれる要素でなければならない。Business作成時、そのSectorがまだ`companyIds`の`sectorIds`に含まれていなければ自動的に追加する
- Business作成時、`driverTree`は指定がなければ`sectorId`の指すSectorの`driverTreeTemplate`をコピーして初期化する（テンプレートが空ならBusinessの`driverTree`も空で始まる）
- `driverTree`の各ノードの`id`はBusiness内で一意。`parentId`は同一Business内の別ノードの`id`を指す（存在しない`parentId`は不可。ルートは`null`）
- `currentSnapshot`はシステムが自動計算するものではなく、Finding/Thought蓄積を踏まえて都度書き直す運用上のフィールド（v1では自動生成ロジックを持たない）
- Businessを削除する場合、その`id`を`driverNodeIds`/`businessIds`で参照する[Thought](thought.md)、`businessId`で参照する[Thesis](thesis.md)が存在するかを確認する（存在する場合は削除不可、または参照解除が必要）

---

## 他ドメインオブジェクトとの関係

- **[Company](company.md)** — 1つのCompanyは複数のBusinessを持つ（多対1、`Business.companyId`）
- **[Sector](sector.md)** — 1つのBusinessは1つのSectorに属する（多対1、`Business.sectorId`）
- **[Thought](thought.md)** — BusinessへのFindingの意味づけは、Thoughtの`businessIds`（および`driverNodeIds`）を介して行う。Business自身はFindingへの参照を持たない
- **[Thesis](thesis.md)** — Thesisは任意で特定のBusinessに紐づけられる（`Thesis.businessId`、任意）。紐づけない場合はCompany全体（複数事業にまたがる、または事業非依存の仮説）を対象とする
- **[Signal](signal.md)** — Signalは直接`businessId`を持たない。事業スコープは`validatesThesisId`が指すThesisの`businessId`から辿る（詳細は[Signal](signal.md)を参照）

---

## 保存フォーマット（大方針）

Businessは `data/vault/businesses/<id>.md` に YAML フロントマター（属性一覧のメタデータ、`driverTree`はYAMLのリストで持つ）＋ Markdown本文（任意）の形で保存する。本文には事業概要など、構造化しにくい背景説明を書いてよい。
