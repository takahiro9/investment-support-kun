# 投資先企業の未来予測・事業戦略提案エージェント — ドメインモデル

## 概要

投資先候補企業について市場動向・事業内容を継続的かつ構造的に把握し、未来予測（この企業はこれからどうなるか）と事業戦略の評価（経営はどんな手を打つべきか／打っているか）の精度を高めるための意思決定支援システムのドメインモデル。

段階的な構築計画（Phase 0〜6）は別途定義する。本ドキュメントはその計画で確定した設計を、各Phaseで作られるエンティティも含めて先に定義したものである。

基本となる層構造:

```
Source（継続監視）→ Finding（事実）→ Thought（解釈）→ Thesis（仮説の統合、ライフサイクルを持つ）
```

この上に、投資ドメイン特有の層を重ねる:

```
Sector / Theme（分類の器）
Company（投資判断の中心単位。ドライバーツリーと現在地スナップショットを持つ）
Thesis（consensusView / variant / whyMispriced / invalidation / confirmation を必須で持つ投資仮説）
  ├─ Signal（時系列指標。Thesisの前提に紐づく）
  ├─ Prediction（時間軸・確度つきの個別予測。答え合わせループ）
  ├─ StrategyRecommendation（経営の打ち手の評価テーブル）
  └─ InvestmentAction（投資家自身の打ち手。終端レイヤー）
```

## エンティティ一覧

| エンティティ | 導入Phase | 役割 |
|---|---|---|
| [Sector](data/sector.md) | Phase 1 | 業種。Companyのマスタ分類、ドライバーツリーのテンプレート単位 |
| [Company](data/company.md) | Phase 1 | 投資判断の中心単位。ドライバーツリーと現在地スナップショットを持つ |
| [Source](data/source.md) | Phase 1 | 情報源。企業/業界/マクロ/市場の4層（+ Theme層はPhase 4） |
| [Finding](data/finding.md) | Phase 1 | 中立な事実のスナップショット。出所区分を持つ |
| [Thought](data/thought.md) | Phase 1 | Findingへの意味づけ。Company/Sector/Themeへの関連付けとドライバーツリーのノード紐付けを担う |
| [Thesis](data/thesis.md) | Phase 2 | 投資仮説。コンセンサス比較・反証/確証条件を必須で持つ |
| [Signal](data/signal.md) | Phase 3 | 時系列指標。Thesisの前提に紐づく |
| [Theme](data/theme.md) | Phase 4 | Sectorを跨ぐマクロ・業界動向の括り |
| [StrategyRecommendation](data/strategy_recommendation.md) | Phase 4 | 経営の打ち手の評価テーブル |
| [InvestmentAction](data/investment_action.md) | Phase 4 | 投資家自身の打ち手（終端レイヤー） |
| [Prediction](data/prediction.md) | Phase 5 | 時間軸・確度つきの個別予測。答え合わせループ |

導入Phaseは「そのエンティティのCRUD・エージェントが実装される段階」を示す。スキーマ自体は本ドキュメントで先に確定しているが、Phase 1で実装するのはSector/Company/Source/Finding/Thoughtのみで、それ以外は各Phaseに到達してから実装する。

## 保存方針

各エンティティは `data/vault/<entity>/<id>.md` にYAMLフロントマター + Markdown本文で保存する（Markdownがsource of truth、検索用のインデックスは派生データとして別途持つ）。書き込みは専用のscript経由でのみ行い、md直接編集は行わない。
