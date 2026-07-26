# Finding から Signal を抽出する (Extract Signal from Finding)

## 目的・概要

`leading`（先行指標: 求人数、設備投資計画、価格改定、代理店動向、業界出荷統計、政策施行スケジュール等）カテゴリの多くは、構造化データAPIには存在せず、決算資料・適時開示・IR説明会資料などの自然言語にしか現れない。システムが `Finding` の本文をLLMで読み取り、そこに含まれる先行指標を `Signal` として抽出する。

## 事前条件

- 抽出対象となる `Finding` が存在し、本文（`body`）を持つこと
- 抽出した値がどの `Thesis` の前提を検証するものかの対応付けが可能であること（対象 Company に少なくとも1つ Thesis が存在すること）

## 事後条件

- 抽出できた先行指標が `Signal`（`extractionMethod = llm_extraction`、`sourceFindingId` に抽出元 Finding を設定）として保存されること

## 基本フロー（正常系）

1. システムは、新規に取得・登録された `Finding`（`leading` カテゴリの情報を含みうる決算資料・IR資料・適時開示等）を対象に、抽出処理をトリガーする。
2. システムは、対象 Finding の本文をLLMで読み取り、先行指標として抽出できる数値（求人数、設備投資計画、価格改定幅等）を検出する。
3. システムは、抽出した各指標について、その Finding が関係する `Company`（`Thought` の `companyIds` を辿って特定、または投資家に確認）に紐づく既存の `Thesis` のうち、その指標が前提を検証しうるものを候補として提示する。
4. 投資家は、提示された候補から `validatesThesisId` を確定し、`validatesAssumption`（何を検証するものか）を確認・編集する。
5. システムは、`Signal` エンティティを `category = leading`、`extractionMethod = llm_extraction`、`sourceFindingId` に抽出元 Finding のIDを設定して作成し、保存する。

## 代替フロー・例外フロー

- **2a. 抽出できる先行指標が本文中に見つからなかった場合:**
  システムは処理をスキップし、Signal を作成しない。
- **3a. 対応付け候補となる Thesis が存在しない場合:**
  システムは抽出結果を保存せず、投資家に「先行指標らしき情報が見つかったが、対応する投資仮説がない」ことを通知する（[Signal の不変条件](../../data/signal.md#不変条件ビジネスルール)により、紐付けのない Signal は作成できない）。
- **4a. 投資家が候補をすべて却下した場合:**
  システムは Signal を作成せず、抽出結果を破棄する。

## 関連するドメインモデル

- [Signal](../../data/signal.md)
- [Finding](../../data/finding.md)
- [Thesis](../../data/thesis.md)
