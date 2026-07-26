# 構造化データAPIから Signal を自動取得する (Fetch Signals from Market Data)

## 目的・概要

システムが定期的に構造化データAPI（証券会社API等）を呼び出し、`market` カテゴリ（株価・バリュエーション・アナリストコンセンサス）および `financial` カテゴリ（売上高・営業利益率等の決算数値）の指標を取得し、`Signal` として蓄積する。この2カテゴリは構造化APIから安価かつ正確に取得できるため、自然言語処理（LLM抽出）を経由しない専用の取得経路を持つ（対照的に `leading` カテゴリの取得は [extract_signal_from_finding](extract_signal_from_finding.md) が担う）。

## 事前条件

- 取得対象となる `Company` が1件以上存在すること
- 各 `Company` について、取得した値がどの `Thesis` の前提を検証するものかの対応付け（`validatesThesisId`/`validatesAssumption`）があらかじめ設定されていること

## 事後条件

- 取得できた指標が `Signal`（`extractionMethod = structured_api`）として保存されること

## 基本フロー（正常系）

1. システムは、一定間隔（例: 日次、または決算発表スケジュールに合わせて）で取得処理をトリガーする。
2. システムは、`market`/`financial` カテゴリの Signal 取得が設定されている `Company` の一覧を取得する。
3. システムは、各 `Company` に対して以下の処理を繰り返す:
   1. 構造化データAPIを呼び出し、対象 `Company` の株価・バリュエーション・決算数値等の最新値を取得する。
   2. 取得した値ごとに、対応する `validatesThesisId`/`validatesAssumption` の設定を参照する。
   3. 同一 `companyId`/`metric`/`period` の Signal が既に存在するかを確認する（重複ではなく改訂履歴として扱うため、存在有無に関わらず新しい Signal として保存してよい）。
   4. `Signal` エンティティを `extractionMethod = structured_api`、`sourceFindingId = null` として作成し、保存する。

## 代替フロー・例外フロー

- **3-1a. APIへのアクセスが失敗した場合（レート制限、認証エラー等）:**
  システムはエラーログを記録し、その Company の処理をスキップして次の Company の処理へ進む。
- **3-2a. 取得した指標に対応する `validatesThesisId`/`validatesAssumption` の設定がない場合:**
  システムはその指標の保存をスキップする（[Signal の不変条件](../../data/signal.md#不変条件ビジネスルール)により、紐付けのない Signal は作成できない）。投資家に「未紐付けの指標がある」ことを通知し、[Record Signal Manually](../investor/record_signal_manually/usecase.md) 等での設定を促す。

## 関連するドメインモデル

- [Signal](../../data/signal.md)
- [Company](../../data/company.md)
- [Thesis](../../data/thesis.md)
