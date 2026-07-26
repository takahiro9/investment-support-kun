# Prediction — 個別予測と答え合わせ

## 概要

Thesisのstatus推移だけでは「予測」にならない（時間軸・確度・観測可能な帰結が無いため）。Thesisから派生する個別の予測を独立エンティティとして持つ。

Phase 1〜4の間は、`type=prediction`の[Thought](thought.md)として自由記述で予測を書き溜める（答え合わせに必要な経過時間を稼ぐため、記録開始自体をPhase 1へ前倒しする）。Phase 5でこれを`Prediction`として構造化する。

**答え合わせ（resolution）を残すこと自体が差別化**。既存の投資リサーチAIも、人間のアナリストの多くも、自分の予測精度を記録していない。これを構造として持つことで「解釈の質」という主観的な概念を、ヒット率・キャリブレーションという測定可能な指標に変換する。

### `observable`の設計（2026-07-26決定: ハイブリッド型）

`observable`は「答え合わせを何によって行うか」を表すフィールド。以下の理由からハイブリッド型に決定した。

- 完全自由記述のみ: 着手コストゼロだが判定が属人化する
- 半構造化タプルのみ: Thesisごとに指標が異なり辞書設計の負担が大きい
- Signal参照型のみ: Signal化されていない事象を表現できない
- イベント型のみ: 数値予測に使えない

ハイブリッド型は、人間可読な自由記述`observableText`を必須フィールドとしつつ、機械判定可能なものだけ任意で`observableRef`（[Signal](signal.md)への参照、または半構造化条件）を添える構成。Signal化されている指標はrefで自動判定、そうでないものはtextのまま人間が答え合わせする、という段階的な移行ができる。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `thesisId` | string (FK) | ✅ | 派生元のThesis |
| `sourceThoughtId` | string (FK) | ❌ | Phase 1〜4で自由記述として書かれていた元Thought（`type=prediction`）。構造化時の由来を追跡する |
| `statement` | string | ✅ | 予測そのもの（例: "FY27Q2までに営業利益率が12%を超える"） |
| `horizon` | date | ✅ | いつまでに、の期限 |
| `probability` | number (0-1) | ✅ | どの程度の確度か |
| `observableText` | string | ✅ | 何をもって答え合わせするかの人間可読な説明（例: "決算短信の営業利益率"） |
| `observableRef` | `ObservableRef` | ❌ | 機械判定可能な場合の参照。Signal化されていなければ設定しない |
| `resolvedAt` | datetime | ❌ | 答え合わせを行った日時。未resolveの間はnull |
| `outcome` | `PredictionOutcome` | ❌ | 結果。`resolvedAt`が設定されて初めて設定できる |
| `postmortem` | string | ❌ | 外した場合、前提のどこが間違っていたか。`outcome`が`miss`/`ambiguous`の場合は必須 |
| `createdAt` | datetime | ✅ | 作成日時 |

---

## 値オブジェクト

### `ObservableRef`

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `signalMetric` | string | ✅ | 参照する[Signal](signal.md)の`metric`名 |
| `comparator` | `>` \| `>=` \| `<` \| `<=` \| `=` | ✅ | 比較演算子 |
| `threshold` | number | ✅ | しきい値 |
| `unit` | string | ❌ | 単位（Signalの`unit`と一致させることが望ましい） |

### `PredictionOutcome`

| 値 | 説明 |
|---|---|
| `hit` | 的中 |
| `miss` | 外れ |
| `ambiguous` | 判定が曖昧（部分的中、観測不能等） |

---

## 不変条件・ビジネスルール

- `thesisId` は必須。1つのPredictionは1つのThesisから派生する（多対1）
- `observableText` は空文字列にできない（`observableRef`があっても、人間可読な説明は必ず残す）
- `outcome`/`postmortem` は `resolvedAt` が設定されるまで設定できない
- `outcome` が `miss` または `ambiguous` の場合、`postmortem` は必須。`hit` の場合は任意
- `horizon` を過ぎても `resolvedAt` が未設定のPredictionは「答え合わせ待ち」として扱う
- `probability` は0以上1以下

---

## 他ドメインオブジェクトとの関係

- **[Thesis](thesis.md)** — Predictionは1つのThesisから派生する（多対1）
- **Thought** — `sourceThoughtId`で、構造化前の自由記述Thoughtを参照してよい（多対1、任意）
- **[Signal](signal.md)** — `observableRef.signalMetric`を通じて間接的に参照する（同一Companyの同名`metric`を持つSignalのうち`period`が`horizon`に対応するものを解決に使う）

---

## 保存フォーマット（大方針）

Predictionは `data/vault/predictions/<id>.md` に YAML フロントマターとして保存する。本文（任意）には予測の背景・前提の詳しい説明を書いてよい。
