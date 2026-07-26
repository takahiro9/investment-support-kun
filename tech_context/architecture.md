# アーキテクチャ

## 方針

本システムは **Claude Code の skill** を UI レイヤーとし、**Markdown ファイル（Vault）** を一次データストアとする CLI ファーストなアプリケーションとして構築する。

データはすべて `data/vault/` 以下の Markdown ファイルに蓄積される。各ファイルは YAML フロントマターで構造化データを持ち、本文に自由形式のテキスト（論証・考察・要約）を記述できる。このファイル群が唯一の真実の源（Single Source of Truth）である。

**Vault は Git 管理対象外とする。** アプリのコード（`scripts/` 等）と、利用者ごとに異なる蓄積データ（投資判断に関わる非公開の考察を含む）を分離するため、Vault も派生インデックスも `data/` ごと `.gitignore` で除外する。

**インデックス（LanceDB 等のベクトル/集計DB）は副次的な導出データとして機能する。** Vault の md ファイルのフロントマターをパースして取り込み、高速な集計クエリやベクトル検索を提供する。インデックスは Vault から再構築できる派生物であり、こちらも Git 管理対象外とする。

---

## レイヤー構成

```
┌─────────────────────────────────┐
│  投資家（ユーザー）              │
└────────────┬────────────────────┘
             │ skill 呼び出し（例: /register-company）
             ▼
┌─────────────────────────────────┐
│  Claude Code Skill Layer        │
│  - 各ユースケースに対応する skill │
│  - 入力の受付・バリデーション     │
│  - 結果の整形・表示              │
└────────────┬────────────────────┘
             │ bash script → uv run python scripts/*.py
             ▼
┌─────────────────────────────────┐
│  Python スクリプト層             │
│  - scripts/*.py                 │
│  - Markdown I/O（frontmatter）  │
│  - インデックス sync            │
│  - JSON 形式で結果を出力         │
└──────────┬─────────────┬────────┘
           │             │
           ▼             ▼
┌──────────────┐  ┌──────────────────────┐
│  data/vault/ │  │  data/index/         │
│  （一次ストア）│  │  （副次インデックス）  │
│  md ファイル  │  │  フロントマターを集約 │
│  Git 管理外   │  │  ベクトル検索・集計   │
│              │  │  Git 管理外          │
└──────────────┘  └──────────────────────┘
```

md ファイル自体（各エンティティのフロントマター + 本文）への読み書き・更新・削除は、必ず専用の Python スクリプト経由で行う。Vault 配下の md を直接編集・作成・削除することは禁止する。インデックスは Vault から導出される派生データであり、スクリプトは Vault への書き込みとインデックス同期を一体で行う。手で md を触るとVaultとインデックスが乖離する。

---

## Vault ストレージ設計

### ディレクトリ構造

```
data/vault/
├── sectors/
│   └── {id}.md
├── companies/
│   └── {id}.md
├── sources/
│   └── {id}.md
├── findings/
│   └── {id}.md
├── thoughts/
│   └── {id}.md
├── theses/
│   └── {id}.md
├── signals/
│   └── {id}.md
├── themes/
│   └── {id}.md
├── strategy_recommendations/
│   └── {id}.md
├── investment_actions/
│   └── {id}.md
└── predictions/
    └── {id}.md
```

各ディレクトリは、それが対応するエンティティの [導入Phase](../domain/README.md#エンティティ一覧) に到達してから実際に書き込まれ始める。スキーマ自体（フロントマター構造）はどのPhaseのエンティティも本ドキュメント群で先に確定させておく。

### フロントマタースキーマ

各 md ファイルは YAML フロントマターで構造化データを持つ。**フィールド名は `domain/data/` のエンティティ定義（camelCase）にそのまま揃え、命名変換層を持たない**（ドメイン定義を唯一の契約とする）。datetime は ISO 8601（UTC）。

エンティティごとの具体的なスキーマ・本文の扱い・バリデーションは、それを書き込むユースケースの `tech_context.md` に記載する。

| エンティティ | Vault パス | スキーマ定義（tech_context.md） |
|---|---|---|
| Sector | `sectors/{id}.md` | [register_sector](../domain/usecase/investor/register_sector/tech_context.md) |
| Company | `companies/{id}.md` | [register_company](../domain/usecase/investor/register_company/tech_context.md) |
| Source | `sources/{id}.md` | [register_source](../domain/usecase/investor/register_source/tech_context.md) |
| Finding | `findings/{id}.md` | [add_finding_manually](../domain/usecase/investor/add_finding_manually/tech_context.md) |
| Thought | `thoughts/{id}.md` | [add_thought](../domain/usecase/investor/add_thought/tech_context.md) |
| Thesis | `theses/{id}.md` | [create_thesis](../domain/usecase/investor/create_thesis/tech_context.md) |
| Signal | `signals/{id}.md` | [record_signal_manually](../domain/usecase/investor/record_signal_manually/tech_context.md) |
| Theme | `themes/{id}.md` | [create_theme](../domain/usecase/investor/create_theme/tech_context.md) |
| StrategyRecommendation | `strategy_recommendations/{id}.md` | [generate_strategy_recommendation](../domain/usecase/investor/generate_strategy_recommendation/tech_context.md) |
| InvestmentAction | `investment_actions/{id}.md` | [create_investment_action](../domain/usecase/investor/create_investment_action/tech_context.md) |
| Prediction | `predictions/{id}.md` | [structure_prediction_from_thought](../domain/usecase/investor/structure_prediction_from_thought/tech_context.md) |

> 本システムはシングルユーザー運用を前提とし、投資家自身を表す独立のエンティティ・認証機構は持たない。「認証済みであること」は環境がその投資家専用に構築されていることを指す。

---

## インデックス（副次インデックス）の役割

インデックスは `data/vault/` の md ファイルを読み込んで構築する派生データである。

### 主な用途

| 用途 | 説明 |
|---|---|
| 集計クエリ | Company ごとの Finding 件数、Sector 別の銘柄一覧、答え合わせ待ち Prediction 件数など |
| 全文検索 | タイトル・本文のキーワード検索 |
| ベクトル検索 | Finding / Thought の意味的な類似検索 |
| 重複チェック | 同一 URL の Finding 登録防止、同一 `ticker` の Company 重複防止 |

### 同期戦略

- **書き込み時同期**: Python スクリプトが md ファイルを書いた直後にインデックスへも反映する
- **再構築**: Vault 全体を再スキャンしてインデックスを再構築するスクリプトを用意する
- インデックスは派生物であるため、削除・再構築が常に安全な操作となる

---

## 各レイヤーの責務

### Skill Layer（Claude Code skill）

- `domain/usecase/` に定義された各ユースケースを 1 skill = 1 ユースケース の粒度で実装する
- skill は Bash ツール経由でシェルスクリプトを呼び出し、シェルスクリプトは `uv run python scripts/*.py` を通じて Python 層を呼び出す
- バリデーション（空文字チェック、重複チェック、不変条件の検査等）は Python スクリプト内で実施する
- 結果は JSON で受け取り、ターミナル上にテーブル形式やリスト形式で整形表示する

### Python スクリプト層

- `scripts/vault.py` — Vault 読み書き（フロントマターパース・md ファイル生成）
- `scripts/index.py` — インデックス接続・スキーマ定義
- `scripts/rebuild_index.py` — Vault 全体を再スキャンしてインデックスを再構築
- エンティティごとの CRUD スクリプト（`scripts/sectors.py` / `scripts/companies.py` / `scripts/sources.py` / `scripts/findings.py` / `scripts/thoughts.py` / `scripts/theses.py` / `scripts/signals.py` / `scripts/themes.py` / `scripts/strategy_recommendations.py` / `scripts/investment_actions.py` / `scripts/predictions.py`）

### Vault（一次ストア）

- `data/vault/` 以下の md ファイルがすべてのデータの正本
- Git 管理対象外（`data/` を `.gitignore` で除外）
- 人間が直接読み書き・編集できる（ただし通常運用ではスクリプト経由に統一する）
- UUID の生成は skill 側（`uuidgen`）で行い、Python スクリプトに渡す
- datetime は ISO 8601 形式（UTC）でフロントマターに記述する

### インデックス（副次データ）

- DB ディレクトリは `data/index/` に配置する（`.gitignore` で管理対象外）
- Vault の md ファイルから派生して構築され、常に再構築可能
- 集計・検索など読み込み系の高速化に特化して使用する

---

## 技術選定の理由

### Markdown ファイル（一次ストア）

- **可読性**: 人間が直接読み書きできる。任意のエディタで開ける
- **移植性**: 特定のデータベースエンジンに依存しない
- **永続性**: フラットファイルのため破損リスクが低く、バックアップも単純
- **Vault as a Knowledge Base**: Finding / Thought / Thesis に本文を自由記述でき、投資判断の思考過程そのものを知識ベースとして育てられる

### インデックス（副次インデックス）

- **ベクトル検索対応**: Finding / Thought の意味的な類似検索を実装できる
- **再構築可能**: Vault から常に再構築できるため、インデックス破損を恐れなくてよい
- **ローカルファイル完結**: サーバー不要で動作する

### uv（パッケージ管理）

- `pyproject.toml` で依存関係をバージョン管理
- `uv run` でプロジェクトの仮想環境を自動的に使用
- `uv.lock` でバージョンを固定し再現性を確保

### Claude Code skill

- ドメインモデルとユースケースが明確に定義済みのため、skill の実装指示が書きやすい
- プロトタイピング段階では UI 開発コストをゼロにできる
- 将来 Web UI が必要になった場合でも、Vault の md ファイルはそのまま流用できる

---

## ディレクトリ構成

```
investment-support-kun/
├── pyproject.toml          # uv プロジェクト定義・依存関係
├── uv.lock                 # 依存関係ロックファイル
├── scripts/                # Python スクリプト層
│   ├── vault.py            # Vault 読み書き（frontmatter パース・md 生成）
│   ├── index.py            # インデックス接続・スキーマ定義
│   ├── rebuild_index.py    # Vault → インデックス再構築
│   ├── sectors.py
│   ├── companies.py
│   ├── sources.py
│   ├── findings.py
│   ├── thoughts.py
│   ├── theses.py
│   ├── signals.py
│   ├── themes.py
│   ├── strategy_recommendations.py
│   ├── investment_actions.py
│   └── predictions.py
├── data/                   # すべて .gitignore 対象（Git 管理外）
│   ├── vault/               # 一次ストア
│   │   ├── sectors/
│   │   ├── companies/
│   │   ├── sources/
│   │   ├── findings/
│   │   ├── thoughts/
│   │   ├── theses/
│   │   ├── signals/
│   │   ├── themes/
│   │   ├── strategy_recommendations/
│   │   ├── investment_actions/
│   │   └── predictions/
│   └── index/               # 副次インデックス（派生・再構築可能）
├── domain/                  # ドメイン定義 Markdown
│   ├── README.md            # ドメインモデル概要・Phase計画とエンティティの対応
│   ├── data/                 # エンティティ定義（ドメインモデル＝唯一の契約）
│   └── usecase/              # ユースケース定義
│       ├── investor/         # 投資家が操作するユースケース
│       │   └── {usecase}/
│       │       ├── usecase.md       # ユースケース仕様（業務フロー）
│       │       └── tech_context.md  # 実装仕様（Vaultパス・スキーマ・バリデーション）※書き込み系のみ
│       └── system/            # システム/自動処理のユースケース
├── tech_context/
│   └── architecture.md      # 本ドキュメント
└── .claude/
    └── skills/               # Claude Code skill 定義
        └── {skill名}/
            ├── SKILL.md
            └── scripts/
```
