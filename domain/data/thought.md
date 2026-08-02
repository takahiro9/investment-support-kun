# Thought — 思考・意味づけ

## 概要

[Finding](finding.md)（中立な事実）に意味を与える解釈層。Finding自体は「何という情報か」しか持たない。「その事実（群）から**何に気づき**、**何（どのCompany/Sector/Theme）に関係し**、**どう役立つか**」という意味づけは、すべてThoughtが引き受ける。

Thoughtは**1つ以上のFindingに根ざす**（`findingIds`）。複数の事実を並べて1つの意見・観察を述べることができる。関連付け先はCompany・Sector・Themeの3種類があり、それぞれ0個以上（`companyIds`/`sectorIds`/`themeIds`）で持つ。考察そのものは**本文（`body`）**に文章として綴る。

Finding↔Company/Sector/Themeの関連はFinding側ではなくThought側に存在する。したがって、あるCompany/Sector/Themeに属するFinding群は**Thoughtを辿って**求める。1つのThoughtを複数のCompany/Sector/Themeに結びつけることもできる。

> 「複数のThoughtを束ねて1つの事業仮説に収斂させる」のは[Thesis](thesis.md)の役割。Thoughtは生の事実（Finding）に直接根ざした解釈で、statusを持たない。Thesisは Thought に根ざした仮説で、statusで育てていく。

### ドライバーツリーのノードへの紐付け

[Company](company.md)のドライバーツリーの各ノードをFindingで埋めていく作業は、Thoughtが`driverNodeIds`を持つことで表現する。あるThoughtが「このFindingはセグメントAの数量に関する情報だ」と意味づけた場合、`companyIds`に対象Companyを、`driverNodeIds`にそのCompanyのツリー内のノードidを入れる。Company・Finding自身はノードへの参照を持たない（関連付けはすべてThoughtが担うという原則を、ドライバーツリーのノードにも適用する）。

### 予測ログ（Phase 1〜4の自由記述）

Phase 5でPredictionエンティティを導入するまでの間、時間軸・確度つきの予測は`type=prediction`のThoughtとして自由記述で書く（「何が・いつまでに・何%くらいで起きると思うか」を`body`に書く）。Phase 5でPredictionへ構造化する際、元になったThoughtは`Prediction.sourceThoughtId`として参照される。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `findingIds` | string[] (FK) | ✅ | 根ざすFinding群（1つ以上） |
| `companyIds` | string[] (FK) | ❌ | 紐づくCompany群（0個以上） |
| `sectorIds` | string[] (FK) | ❌ | 紐づくSector群（0個以上） |
| `themeIds` | string[] (FK) | ❌ | 紐づくTheme群（0個以上、Phase 4以降） |
| `driverNodeIds` | string[] | ❌ | 紐づくCompanyのドライバーツリーのノードid群（`companyIds`が指すCompanyのツリー内のノードを指す） |
| `type` | `ThoughtType` | ✅ | Thought種別 |
| `body` | string | ✅ | 本文。気づき・予測・問いを文章で綴る |
| `createdAt` | datetime | ✅ | 作成日時 |
| `tags` | string[] | ❌ | 分類用の自由記述タグ |

---

## 値オブジェクト

### `ThoughtType`

| 値 | 呼称 | 説明 |
|---|---|---|
| `note` | 発見 | Finding群から得た気づき・観察・主張 |
| `question` | 疑問 | Finding群から生まれた、探求したい問い・引っかかり |
| `prediction` | 予測 | Phase 5でPredictionへ構造化するまでの、自由記述の時系列予測（「何が・いつまでに・何%くらいで起きると思うか」） |

---

## 不変条件・ビジネスルール

- `findingIds` は1つ以上（事実に根ざさないThoughtは作らない）
- `body` は空文字列にできない
- 1つのFindingに複数のThoughtを付与可能（種別が異なるものも、同種のものも可）
- `companyIds`/`sectorIds`/`themeIds` はすべて空でもよい（関連付けを持たないThoughtも許容する）が、実務上は少なくとも1つに紐づけることが推奨される
- `driverNodeIds` を指定する場合、`companyIds` に対応するCompanyが含まれていること（ドライバーツリーのノードは特定Companyのツリーに属するため）
- `type=prediction` のThoughtは、Phase 5以降 `Prediction.sourceThoughtId` から参照されることがある。参照後もThought自体は削除されない（元の自由記述ログとして残す）

---

## 他ドメインオブジェクトとの関係

- **Finding** — Thoughtは1つ以上のFindingに根ざす（多対多）。Findingを削除すると、そのFindingは各Thoughtの`findingIds`から除かれ、根拠を失ったThoughtは削除される
- **Company / Sector / Theme** — `companyIds`/`sectorIds`/`themeIds`を介して関連付ける。Company/Sector/Theme↔Findingの関連はこのThoughtを介してのみ成立する
- **[Thesis](thesis.md)** — 複数のThoughtが束ねられて1つのThesis（事業仮説）へ収斂する（多対多）。1つのThoughtは複数のThesisに属してよい。束ね先はThesis側の`thoughtIds`が持つ
- **[Prediction](prediction.md)** — `type=prediction`のThoughtは、Phase 5での構造化時に`Prediction.sourceThoughtId`として参照されうる

---

## 保存フォーマット（大方針）

Thoughtは `data/vault/thoughts/<id>.md` に **YAML フロントマター + Markdown本文（必須）** の形で保存する。
