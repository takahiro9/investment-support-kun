# Signal — 時系列指標

## 概要

売上高・営業利益率などの数値は、テキストのFinding/Thoughtだけでは追跡しづらい。決算資料・業界統計等から抽出した数値を時系列データポイントとして別立てで保持する。

| `category` | 例 | 特性 |
|---|---|---|
| `financial` | 売上高、営業利益率、KPI推移 | 遅行。決算に出た時点で確定する数値 |
| `operational` | 出荷台数、稼働率、受注残、解約率 | やや先行 |
| `leading` | 求人数、設備投資計画、価格改定、代理店動向、業界出荷統計、政策施行スケジュール | 先行。予測の精度に直結 |

抽出優先順位はleadingを先行させる（financialは後回しでよい）。

### 抽出元

`financial`は構造化データAPI（EDINET等）を優先する——安価かつ正確に取得できるため。一方`leading`（設備投資計画・価格改定・経営者コメントのトーン変化等）は決算資料・適時開示・IR説明会資料などの**自然言語にしかない情報**であることが多く、LLMによる自然言語処理（Findingの本文からの抽出）を前提とする。「構造化APIを優先し自然言語は補完」ではなく、**Signal種別ごとに主たる抽出元が異なる**という設計になる。

### Thesisの前提への紐付け

Signalは単体では意味を持たない。「この指標はThesisのどの前提を検証するためのものか」を`validatesThesisId`/`validatesAssumption`で明示的に紐づける。紐付けのないSignalは「何のために見ているか分からない時系列データ置き場」になるため、この紐付けを必須とする。

### 事業（Business）単位への紐付け方

Signal自身は`businessId`のようなフィールドを直接持たない。事業スコープは常に`validatesThesisId`が指す[Thesis](thesis.md)の`businessId`経由で辿る——Thesisが特定のBusinessに紐づいていればそのSignalも事業固有、Thesisが（`businessId`なしで）Company全体を対象にしていればそのSignalも会社全体の指標、という扱いになる。

同じ実測値が複数の事業に関するThesisの前提をそれぞれ検証する場合（例: ある為替感応度の数値が、事業Aの原価前提と事業Bの原価前提の両方を検証する）は、`businessIds`のような多対多FKを持たせるのではなく、**Signalレコード自体を事業の数だけ複製し、それぞれ異なる`validatesThesisId`/`validatesAssumption`を持たせる**。Signalが「値そのもの」ではなく「値＋どの仮説の前提を検証するかという意味づけ」の組で初めて意味を持つという設計原則（Finding/Thoughtの関係と同型）に従うと、1つの値が2つの仮説の前提を検証するなら、それは2つの異なるSignalとして存在するのが一貫している。この複製は、既存の「同一`companyId`/`metric`/`period`の組み合わせで複数のSignalを持つことを許容する」という不変条件（下記参照）で元々サポートされている。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `companyId` | string (FK) | ✅ | 対象Company |
| `category` | `SignalCategory` | ✅ | 指標の分類 |
| `metric` | string | ✅ | 指標名（例: `operating_margin`、`job_postings_count`） |
| `period` | string | ✅ | 対象期間・時点（例: `2027Q2`、日次データの場合は日付） |
| `value` | number | ✅ | 値 |
| `unit` | string | ❌ | 単位（例: `%`、`件`、`円`） |
| `sourceFindingId` | string (FK) | ❌ | 抽出元のFinding。構造化APIから直接取得した場合はnullでもよい |
| `extractionMethod` | `ExtractionMethod` | ✅ | どう取得した値か |
| `validatesThesisId` | string (FK) | ✅ | この指標が前提を検証する対象のThesis |
| `validatesAssumption` | string | ✅ | Thesisのどの前提を検証するものかの説明（自由記述） |
| `createdAt` | datetime | ✅ | 作成日時 |

---

## 値オブジェクト

### `SignalCategory`

上記「概要」の表を参照（`financial` / `operational` / `leading`）。

### `ExtractionMethod`

| 値 | 説明 |
|---|---|
| `manual` | 人間がFindingを読んで手入力 |
| `llm_extraction` | Findingの自然言語本文からLLMで抽出 |
| `structured_api` | EDINET等の構造化データソースから直接取得 |

---

## 不変条件・ビジネスルール

- `companyId`/`validatesThesisId` は必須。紐付けのないSignalは作成できない（「何のために見ているか分からない時系列データ置き場にしない」という設計方針を型で強制する）
- `validatesThesisId` が指すThesisは、`companyId` が指すのと同じCompanyのThesisであること
- `extractionMethod=structured_api` の場合、`sourceFindingId` はnullでよい。`llm_extraction`/`manual` の場合は、可能な限り`sourceFindingId`を設定する（追跡可能性のため必須ではないが推奨）
- 同一`companyId`/`metric`/`period`の組み合わせで複数のSignalを持つことは許容する（改訂・再取得による上書きではなく、履歴として積み上げる）

---

## 他ドメインオブジェクトとの関係

- **Company** — Signalは1つのCompanyに紐づく（多対1）
- **[Business](business.md)** — Signalは直接のFKを持たず、`validatesThesisId`が指すThesisの`businessId`を介して間接的に事業スコープを持つ
- **[Thesis](thesis.md)** — Signalは1つのThesisの前提を検証する（多対1、`validatesThesisId`）
- **Finding** — 抽出元としてFindingを参照してよい（多対1、任意）

---

## 保存フォーマット（大方針）

Signalは `data/vault/signals/<id>.md` に YAML フロントマターとして保存する（本文は基本的に使わない。時系列の1データポイントであり、論証を持たないため）。
