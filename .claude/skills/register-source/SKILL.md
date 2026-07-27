---
name: register-source
description: Register a new Source (情報源) to continuously monitor in the investment vault — an IR feed, disclosure feed, industry publication, or market-data API. Use when the investor wants to add a recurring information pipeline, not a single document.
---

# 情報源を登録する (Register Source)

Spec: `domain/usecase/investor/register_source/usecase.md`, `domain/usecase/investor/register_source/tech_context.md`

## Source か Finding かの判定（最初に必ず行う）

登録対象を時間をおいて再取得したとき、「新着項目の一覧」が返ってくる可能性があるか投資家に確認する（`domain/data/source.md#source-か-finding-かの判定`）。

- Yes（適時開示フィード、IR RSS、業界紙の一覧、市場データAPIなど）→ このスキルで Source として登録する。
- No（1本の決算短信PDF、1本のニュース記事など単発・静的なコンテンツ）→ Source としては登録せず、`add-finding` skill を案内する。

## 手順

1. 投資家に以下を確認する:
   - `type`: `rss_feed` / `web_page` / `youtube_channel` / `disclosure_feed` / `market_data_api` / `newsletter`
   - `layer`: `company` / `sector` / `theme` / `macro` / `market`
   - `layer` に応じた参照先（`layer` が `company`/`market` なら `companyId`、`sector` なら `sectorId`、`theme` なら `themeId`）。id が分からなければ `list-companies` / `list-sectors` / `list-themes` skill で引く。
   - `name`（表示名）、`url`、任意で `description`
2. UUID を生成する: `uuidgen`
3. 以下を実行する:
   ```
   uv run python scripts/sources.py register --id <uuid生成結果> \
     --type "<type>" --layer "<layer>" \
     [--company-id "<companyId>"] [--sector-id "<sectorId>"] [--theme-id "<themeId>"] \
     --name "<name>" --url "<url>" [--description "<description>"]
   ```
4. 終了コードで分岐する:
   - **exit 1**（stderr `{"errors": [...]}`）: バリデーションエラー。よくある原因 — `name`/`url` が空、`layer` に応じた参照先が未指定または存在しない、同一 `url` が登録済み。エラー内容を伝え、再入力を促す。
   - **exit 2**（stderr `{"warning": "...", "requiresForce": true}`）: URL への疎通確認に失敗した警告。内容を投資家に伝え、(a) URL を修正して再実行するか、(b) 警告を無視して登録を強行するかを選ばせる。(b) の場合は同じコマンドに `--force` を付けて再実行する。
   - **exit 0**: 成功。stdout の JSON（登録された Source）をもとに登録完了を伝える。

## 注意

- `data/vault/sources/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
- `status` は登録時に自動で `active` になる。取得停止・アーカイブの操作は本 skill の対象外。
