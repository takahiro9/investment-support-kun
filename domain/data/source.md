# Source — 情報源

## 概要

あらかじめ登録した情報の取得元。「どこから情報を集めるか」を明示的に管理することで、収集範囲を意図的にコントロールできる。

Sourceの本質は**「流れ」**にある。一度登録すれば、取得のたびに新しいコンテンツ（Finding）を0〜N件**生み出し続ける、継続的な監視対象**である。逆に、再取得しても同じものしか返さない単発・静的なコンテンツはSourceではなく[Finding](finding.md)として扱う。

「この情報源を監視して、関連するFindingを蓄積する」という情報収集パイプラインの入口となる。

Sourceが紐づく範囲（スコープ）は、下記のとおり層に分ける。

| レイヤー(`layer`) | スコープ | Source例 |
|---|---|---|
| `company` | 個別Company | IR RSS、決算説明資料、EDINET/TDnetの適時開示 |
| `sector` | Sector | 業界紙・業界団体レポート、サプライチェーン上下流のニュース |
| `theme` | Theme | 複数Sectorを跨ぐ政策・サプライチェーン動向 |
| `macro` | 全体共通 | 政策（官公庁の規制・補助金動向）、社会動向（人口動態、消費トレンド、技術トレンド） |

`company`層・`sector`層・`theme`層のFindingは、それぞれ紐づく単位（Company/Sector/Theme）を跨いで参照されうる。特に`sector`層・`macro`層・`theme`層のFindingは、複数のCompanyのThesisから共通して参照される想定（1つの業界動向・政策ニュースが複数銘柄のThesisに影響しうる）。

---

## Source か Finding かの判定

ある情報をSourceとして登録すべきか、それとも単一の[Finding](finding.md)として保存すべきかは、次のリトマス試験で判定する。

> **その対象を時間をおいて再取得したとき、「新着項目の一覧」が返ってくる可能性があるか？**
>
> - **Yes → Source（流れ）** … IR RSS、適時開示フィード、業界紙のニュース一覧など。再取得すると新着が増えていく。
> - **No → Finding（スナップショット）** … 1本の決算説明資料PDF、1本のニュース記事など。再取得しても同じものが返る。

例:

- `https://www.release.tdnet.info/...`（適時開示が流れてくるフィード）→ **Source**
- 特定の1件の決算短信PDF → **Finding**

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `type` | `SourceType` | ✅ | 情報源の種別 |
| `layer` | `SourceLayer` | ✅ | スコープ層 |
| `companyId` | string (FK) | △ | `layer`が`company`のとき必須 |
| `sectorId` | string (FK) | △ | `layer`が`sector`のとき必須 |
| `themeId` | string (FK) | △ | `layer`が`theme`のとき必須 |
| `name` | string | ✅ | 表示名 |
| `url` | string | ✅ | 情報源のURLまたは識別子 |
| `description` | string | ❌ | メモ・補足説明 |
| `status` | `SourceStatus` | ✅ | 有効状態 |
| `lastFetchedAt` | datetime | ❌ | 最後に情報を取得した日時 |
| `createdAt` | datetime | ✅ | 登録日時 |
| `updatedAt` | datetime | ✅ | 最終更新日時 |

---

## 値オブジェクト

### `SourceType`

| 値 | 説明 |
|---|---|
| `rss_feed` | RSS / Atom フィード |
| `web_page` | RSSを持たないが、新着コンテンツが一覧・追加されていくWebページ（スクレイピング対象） |
| `youtube_channel` | YouTubeチャンネル（決算説明会の録画配信等） |
| `disclosure_feed` | EDINET/TDnet等の適時開示フィード |
| `newsletter` | メールニュースレター |

### `SourceLayer`

| 値 | スコープ | 必須になる参照 |
|---|---|---|
| `company` | 個別Company | `companyId` |
| `sector` | Sector | `sectorId` |
| `theme` | Theme | `themeId` |
| `macro` | 全体共通 | なし |

### `SourceStatus`

| 値 | 説明 |
|---|---|
| `active` | 有効（定期的に取得対象） |
| `paused` | 一時停止（取得をスキップ） |
| `archived` | アーカイブ済み（参照のみ可能） |

---

## 不変条件・ビジネスルール

- Sourceは「再取得すると新着が生まれうる流れ」であること（→[Sourceか Findingかの判定](#source-か-finding-かの判定)）。単発・静的なコンテンツはSourceとして登録せず、Findingとして保存する
- `layer`に応じて必須になる参照が異なる（上表）。対応しない参照フィールド（例: `layer=macro`のときの`companyId`）は設定しない
- `name` は空文字列にできない
- `url` はシステム全体で一意
- `status`が`active`のSourceのみ情報取得処理の対象となる

---

## 他ドメインオブジェクトとの関係

- **Company** — `layer=company`のSourceはCompanyに紐づく
- **Sector** — `layer=sector`のSourceはSectorに紐づく
- **Theme** — `layer=theme`のSourceはThemeに紐づく
- **Finding** — Sourceからの取得によってFindingが生成される。生成されたFindingは取得元Sourceへの関連（FK）を持たず、出所は`url`/`sourceUrl`に記録されるのみ

---

## 保存フォーマット（大方針）

Sourceは `data/vault/sources/<id>.md` に YAML フロントマターとして保存する。本文は任意。
