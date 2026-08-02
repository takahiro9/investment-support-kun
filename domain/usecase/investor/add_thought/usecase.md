# Thought を追加する (Add Thought)

## 目的・概要

投資家が `Finding`（中立な事実）に意味づけを与える。1つ以上の Finding に根ざし（`findingIds`）、それが何（どの `Company` / `Sector` / `Theme`）に関係するかを結びつけ、必要なら対象 Company の [ドライバーツリー](../../../data/company.md#ドライバーツリー事業構造の骨格)のどのノードを埋めるものかも指定する。考察そのものは本文（`body`）に文章として綴る。

種別（`type`）によって考察の性質が変わる:

- `note` — Finding群から得た気づき・観察・主張
- `question` — Finding群から生まれた、探求したい問い・引っかかり
- `prediction` — 時間軸・確度つきの予測を自由記述で書く（「何が・いつまでに・何%くらいで起きると思うか」を本文に書く。この中から重要なものを後で [Prediction](../../../data/prediction.md) として構造化する）

## 事前条件

- 対象となる1つ以上の `Finding` が存在すること
- `companyIds` / `sectorIds` / `themeIds` を指定する場合、それぞれの対象が存在すること

## 事後条件

- 新しい `Thought` が対象の `Finding` 群に紐づいて保存されること
- `companyIds` / `sectorIds` / `themeIds` を指定した場合、それらの Finding がその Company / Sector / Theme に結びつくこと

## 基本フロー（正常系）

1. 投資家は、意味づけの起点となる1つ以上の `Finding` を選択する。
2. 投資家は、Thought の種別（`note` / `question` / `prediction`）を選ぶ。
3. 投資家は、本文（`body`）に考察を綴る。
4. 投資家は、任意でこの Thought が関係する `Company` / `Sector` / `Theme` を選択する。対象 Company のドライバーツリーの特定ノードを埋めるものであれば、そのノード（`driverNodeIds`）も選択する。
5. システムは、`body` が空でないこと、`driverNodeIds` を指定する場合は対応する `companyIds` が含まれていることを検証する（[Thought の不変条件](../../../data/thought.md#不変条件ビジネスルール)）。
6. システムは、新しい `Thought` エンティティを作成し、保存する。
7. システムは、Finding の画面上に新しく追加された Thought を表示し、対象 Company のドライバーツリー上で該当ノードが埋まったことを反映する。

## 代替フロー・例外フロー

- **3a. `body` が空の場合:**
  システムは保存処理を行わず、入力を求めるエラーを表示する。
- **4a. `driverNodeIds` を指定したが対応する `companyIds` が選ばれていない場合:**
  システムはエラーを返し、対象 Company の選択を求める。
- **4b. どの Company / Sector / Theme にも関係づけない場合:**
  システムは関連付けなしでの保存を許容する（推奨はしないが必須ではない）。

## 関連するドメインモデル

- [Thought](../../../data/thought.md)
- [Finding](../../../data/finding.md)
- [Company](../../../data/company.md)
