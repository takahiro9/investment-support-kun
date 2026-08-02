# 投資先企業の未来予測・事業戦略提案エージェント — ドメインモデル

## 概要

対象企業の事業構造・意思決定構造を継続的かつ構造的に理解する（「経営ならこの状況をどう判断するか」を再現できる解像度まで掘り下げる）ことを主目的とするドメインモデル。投資判断の精度向上（未来予測・市場との比較）は、この理解が十分に深まった結果として得られる副産物として位置づける。投資家自身が唯一の使い手であり続ける前提のもと、「投資家としてどう賭けるか」を先に問うのではなく、「企業・事業の実態はどうで、経営ならどう動くか」を先に問う順序にドメインモデルを合わせている。

基本となる層構造:

```
Source（継続監視）→ Finding（事実）→ Thought（解釈）→ Thesis（仮説の統合、ライフサイクルを持つ）
```

この上に、投資ドメイン特有の層を重ねる:

```
Sector / Theme（分類の器）
Company（意思決定理解の中心単位。ドライバーツリーと現在地スナップショットを持つ）
Thesis（事業理解の仮説。何が実態で、なぜそう言えるか、何が起きたら崩れる／確からしくなるか [invalidation / confirmation] を常に必須で持つ）
  ├─ Signal（時系列指標。Thesisの前提に紐づく）
  ├─ Prediction（時間軸・確度つきの個別予測。答え合わせループ）
  ├─ StrategyRecommendation（経営の打ち手の評価テーブル。実行確率・インパクトのみを持つ）
  └─ InvestmentAction（投資家自身の打ち手。Company理解が十分深まった結果として最後に一段足す終端レイヤー）
```

### 目的と副産物の関係

Thesis/StrategyRecommendationはいずれも「事業・経営の実態理解」に純化しており、市場コンセンサスとの比較や織り込み度といった投資家固有の判断材料は持たない。企業・事業の実態と経営の意思決定構造を理解すること自体を主目的とし、それを踏まえた投資家自身の打ち手は最後に[InvestmentAction](data/investment_action.md)が一段足す。

詳細は各エンティティ定義（[thesis.md](data/thesis.md)、[strategy_recommendation.md](data/strategy_recommendation.md)）を参照。

## エンティティ一覧

| エンティティ | 役割 |
|---|---|
| [Sector](data/sector.md) | 業種。Companyのマスタ分類、ドライバーツリーのテンプレート単位 |
| [Company](data/company.md) | 投資判断の中心単位。ドライバーツリーと現在地スナップショットを持つ |
| [Source](data/source.md) | 情報源。企業/業界/マクロ/Themeの各層を監視する |
| [Finding](data/finding.md) | 中立な事実のスナップショット。出所区分を持つ |
| [Thought](data/thought.md) | Findingへの意味づけ。Company/Sector/Themeへの関連付けとドライバーツリーのノード紐付けを担う |
| [Thesis](data/thesis.md) | 事業仮説。反証/確証条件を必須で持つ |
| [Signal](data/signal.md) | 時系列指標。Thesisの前提に紐づく |
| [Theme](data/theme.md) | Sectorを跨ぐマクロ・業界動向の括り |
| [StrategyRecommendation](data/strategy_recommendation.md) | 経営の打ち手の評価テーブル |
| [InvestmentAction](data/investment_action.md) | 投資家自身の打ち手（終端レイヤー） |
| [Prediction](data/prediction.md) | 時間軸・確度つきの個別予測。答え合わせループ |

## 保存方針

各エンティティは `data/vault/<entity>/<id>.md` にYAMLフロントマター + Markdown本文で保存する（Markdownがsource of truth、検索用のインデックスは派生データとして別途持つ）。書き込みは専用のscript経由でのみ行い、md直接編集は行わない。
