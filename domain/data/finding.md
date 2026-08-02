# Finding — 発見・知見

## 概要

「気になった情報アイテム」の最小単位であり、**文脈を持たない事実のスナップショット**。登録された情報源（[Source](source.md)）から自動収集されたものに限らず、手動で登録した記事・メモ・適時開示なども含む、気になった対象全般を受け止める器である。Web記事・メモ・PDF・適時開示など多様な形式の情報を統一的に扱う。

Finding自体は **「何という情報か」だけ**を中立的に保持し、Company/Sector/Theme/Sourceへの関連は持たない。「この事実が何（どのCompany/Sector/Theme）に関係し、どんな根拠でどう役立つか」という**意味づけはすべて[Thought](thought.md)が担う**。出所は`url`/`sourceUrl`に残るが、それはFK関連ではなく単なる記録である。

[Source](source.md)（流れ）に対して、Finding は **ある時点で捉えた1個のスナップショット**。ある情報をSourceとすべきかFindingとすべきかの判定は[Sourceか Findingかの判定](source.md#source-か-finding-かの判定)を参照。

投資ドメイン特有の拡張として、**出所区分**（`evidenceTier`）を最初から付与する。企業発信のFindingは構造的にポジティブに偏るため、Thoughtがそのまま企業の言い分の要約にならないよう、区分を明示して確証バイアスの混入経路を可視化する。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `type` | `FindingType` | ✅ | Finding種別 |
| `title` | string | ✅ | タイトル |
| `url` | string | ❌ | 元URL（`web_article`/`youtube`/`disclosure`の場合） |
| `body` | string | ❌ | テキスト本文（`memo`の場合など） |
| `sourceUrl` | string | ❌ | 実際にコンテンツを取得したページのURL（Sourceのトップページとは異なる） |
| `evidenceTier` | `EvidenceTier` | ✅ | 出所区分。企業発信の偏りを可視化するため最初から必須にする |
| `savedAt` | datetime | ✅ | 保存日時 |
| `contentUpdatedAt` | datetime | ❌ | コンテンツの最終更新日時（適時開示の公表日時など、情報源が提供する更新日時。不明な場合はnull） |
| `tags` | string[] | ❌ | 分類用の自由記述タグ（0個以上、複数可） |

---

## 値オブジェクト

### `FindingType`

| 値 | 説明 |
|---|---|
| `web_article` | Webページ・記事（業界紙・ニュース等） |
| `memo` | 手入力したメモ |
| `pdf` | PDFファイル（決算説明資料等） |
| `youtube` | YouTube動画（決算説明会の録画等） |
| `image` | 画像ファイル |
| `disclosure` | 適時開示・決算短信そのもの |
| `link` | 上記に当てはまらない、気になったWeb上の対象 |

### `EvidenceTier`

| 値 | 説明 |
|---|---|
| `primary_disclosure` | 一次情報（適時開示・決算短信・有価証券報告書など） |
| `company_issued` | 企業発信（IR説明会資料、広報発表など。一次情報ほど厳格でないが企業側の発信） |
| `third_party` | 第三者（業界紙・競合・顧客・アナリストレポートなど） |
| `inference` | 推測（一次情報からの推論・憶測。裏付けが弱いものを明示的に区別する） |

---

## 不変条件・ビジネスルール

- `type` が `web_article` / `youtube` / `disclosure` / `link` の場合、`url` は必須
- `type` が `memo` の場合、`body` は必須
- 同一`url`のFindingを重複登録することは不可（システム全体で`url`は一意）
- 手動で追加するFindingには、[Thought](thought.md)を1つ以上付与しなければならない（その事実が何に関係し、どう役立つかを記録するため）。Sourceからの自動取得で生まれるFindingは未整理のraw状態でよく、Thoughtは後から付与する
- `evidenceTier` は必須。省略不可（後から付け直すコストが高いため、登録フローの最初の段階で必ず選ばせる）

---

## 他ドメインオブジェクトとの関係

- **Thought** — Findingには複数のThoughtを付与できる（1対多）。FindingをCompany/Sector/Themeに結びつけ、意味づける役割はすべてThoughtが担う
- **Company / Sector / Theme** — Findingはこれらと直接の関連を持たない。両者はThought（`companyIds`/`sectorIds`/`themeIds`等）を介して間接的に結びつく
- **Source** — Findingは取得元Sourceへの関連を持たない。Sourceは定期取得を通じてFindingを生成するが、生成されたFindingは出所を`url`/`sourceUrl`に記録するのみ
- **[Signal](signal.md)** — SignalはFindingから抽出された数値を保持するとき、抽出元として`sourceFindingId`でFindingを参照してよい（Signal側からの一方向の参照。Finding側はSignalへの関連を持たない）

---

## 保存フォーマット（大方針）

Findingは `data/vault/findings/<id>.md` に **YAML フロントマター + Markdown本文** の形で保存する。

- **フロントマター（必須）**: 上記「属性一覧」のメタデータを格納する。機械可読な単一の正本（Source of Truth）。
- **フロントマターの外側（Markdown本文、任意）**: その Finding の情報源そのものの内容を整理したMarkdown。構造上は任意で、Sourceからの自動取得やURLのみの手動追加では空のまま生まれてよい。一方、内容を整理できた場合は、後から人間がこのファイル単体を読むだけで元コンテンツの要点・構造・引用に当たれるよう本文を記載することが望ましい。

### 本文に書くべきこと

- 情報源コンテンツの本文を構造化したMarkdown（見出し・段落・箇条書き・コードブロック等を活用）。
  - `web_article` / `pdf` / `disclosure`: 記事・開示資料を読み取った上で、見出し構造を維持しつつ要点を整理。重要な箇所は引用ブロックで残す。
  - `youtube`: タイトル、説明欄、トランスクリプトの要点、章立て（チャプター）など。
  - `memo`: 入力した本文をそのまま。
  - `link`: 対象ページから読み取れる要点を整理。
  - `image`: 画像の説明・OCRテキスト・キャプション等。
- 一次情報のURL・参照リンクは本文中にも明記する（フロントマターの`url`だけに頼らない）。

### 書かないこと

- 個人の感想・解釈・問いは本文に書かない（それらは[Thought](thought.md)として別途記録する）。本文はあくまで情報源の内容を整理した中立的な記録に留める。
