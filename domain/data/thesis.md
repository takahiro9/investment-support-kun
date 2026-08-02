# Thesis — 事業仮説

## 概要

複数の[Thought](thought.md)（意味づけ）を束ね、一つの**事業理解の仮説へ収斂させる統合層**。層構造の最上段に位置する。

```
Finding（事実）→ Thought（意味）→ Thesis（事業仮説への統合）
```

Thoughtが**1つ以上のFindingに根ざした注釈**であるのに対し、Thesisは**複数のThoughtから成る**（多対多）。単一の出所を持たず、散らばった意味づけが収斂して立ち上がる主張がThesisである。証拠の単位をFindingではなくThoughtに取るのは、裸のFindingはスタンスを持たず、意味づけ（スタンス）はすべてThoughtが担うという原則に従うため。

Thesisは時間とともに育つ。証拠（Thought）が積み重なるにつれ`status`が遷移し、`updatedAt`が更新される、認識論的ライフサイクルを持つ。

Thesisは**事業理解の仮説**である。「何が実態で、なぜそう言えるか、何が起きたら崩れる／確からしくなるか」（`invalidation`/`confirmation`）は常に必須で、これは投資という文脈を離れても成立する経営理解そのものである。

反証条件（`invalidation`）と確証条件（`confirmation`）は対で必須（反証条件のみだと判定基準が片側に偏り、statusを前進させる方向にしか働かなくなる）。両方とも**自然言語の自由記述**として持つ（指標名・閾値・比較演算子への半構造化は将来の論点として保留）。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `companyId` | string (FK) | ✅ | この仮説が対象とするCompany |
| `statement` | string | ✅ | 仮説を一言で表した見出し（例: "この企業はこうなる"） |
| `invalidation` | string | ✅ | 何が起きたら崩れるか（反証条件、自由記述） |
| `confirmation` | string | ✅ | 何が起きたら確度が上がるか（確証条件、自由記述） |
| `horizon` | date | ❌ | いつまでの時間軸を想定した仮説か（個別の予測時期はPredictionで扱うため、ここでは目安） |
| `probability` | number (0-1) | ❌ | 仮説全体の確度の目安（個別予測の確度はPredictionで扱う） |
| `status` | `ThesisStatus` | ✅ | 認識論的ライフサイクルの状態 |
| `thoughtIds` | string[] (FK) | ✅（空可） | この仮説を構成するThought群 |
| `body` | string | ✅ | 論証本文。なぜ束ねたThought群からこの`statement`が立つのか |
| `createdAt` | datetime | ✅ | 作成日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |
| `tags` | string[] | ❌ | 分類用の自由記述タグ |

### 将来の拡張（未実装）

- `scenarios: Scenario[]` — bull/base/bearのシナリオ（`case` / `trigger` / `probability` / `targetPrice`）をThesisに付与し、InvestmentActionのポジションサイジングと接続する

---

## 値オブジェクト

### `ThesisStatus`

証拠が溜まるにつれて遷移する、仮説の成熟度。

| 値 | 説明 |
|---|---|
| `seed` | 萌芽。思いつき・問いの段階 |
| `developing` | 育成中。Thoughtを束ねながら検証・肉付けしている最中 |
| `established` | 確立。十分なThoughtに支持され、statement/invalidation/confirmationが実用的な粒度で書けている |
| `challenged` | 要レビュー。invalidation条件に抵触した際にまずここへ置く。一時的なノイズか本質的な崩れかを人間が見極めてから`dropped`または復帰を判断する |
| `dropped` | 棄却。反証された、あるいは追わないことにした |

---

## 不変条件・ビジネスルール

- `companyId` は必須。1つのThesisは1つのCompanyに紐づく（多対1）。1つのCompanyは複数のThesisを持ってよい
- `statement`/`invalidation`/`confirmation`/`body` はいずれも空文字列にできない（`status`によらず常に必須。事業理解の仮説として成立するための最低条件）
- `invalidation`/`confirmation` は自然言語の自由記述として持つ（半構造化はしない）
- `status` の遷移は人間が判断する（v1では自動遷移ロジックを持たない）。invalidation抵触時はまず`challenged`に置き、即座に`dropped`にはしない
- `thoughtIds` の要素に重複は持たない。1つのThoughtは複数のThesisに属してよい（多対多）
- `probability` を指定する場合は0以上1以下

---

## 他ドメインオブジェクトとの関係

- **Company** — Thesisは必ずひとつのCompanyについての仮説（多対1）
- **Thought** — Thesisは複数のThoughtから構成される（多対多）
- **[Signal](signal.md)** — SignalはThesisの前提に`validatesThesisId`で紐づく（多対1）
- **[Prediction](prediction.md)** — PredictionはThesisから派生する個別の予測（多対1、`Prediction.thesisId`）
- **[StrategyRecommendation](strategy_recommendation.md) / [InvestmentAction](investment_action.md)** — Thesisを踏まえて生成される（任意の弱い参照、`relatedThesisIds`）

---

## 保存フォーマット（大方針）

Thesisは `data/vault/theses/<id>.md` に **YAML フロントマター + Markdown本文（論証、必須）** の形で保存する。

- **フロントマター（必須）**: 上記「属性一覧」のメタデータ。`thoughtIds`はYAMLのリストで持つ。
- **フロントマターの外側（Markdown本文、必須）**: 仮説の論証・展開。なぜこのThought群からこの`statement`が立つのか、その組み立てを文章で綴る。Thesisは`statement`の見出しだけでなく、この本文をもって初めて成立する。
