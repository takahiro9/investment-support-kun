---
name: add-finding
description: Add a Finding (手動で発見した情報アイテム) to the investment vault as a neutral fact snapshot — an article, PDF, disclosure, memo, or market-data point. Use when the investor found something worth saving, then always follow up with a Thought.
---

# Finding を手動で追加する (Add Finding Manually)

Spec: `domain/usecase/investor/add_finding_manually/usecase.md`, `domain/usecase/investor/add_finding_manually/tech_context.md`

## Source か Finding かの判定（最初に必ず行う）

登録対象の URL を時間をおいて再取得したとき、「新着項目の一覧」が返ってくる可能性がある場合（適時開示フィード、市場データAPIなど）は Finding ではなく `register-source` skill を案内する（`domain/data/source.md#source-か-finding-かの判定`）。単発・静的なコンテンツ（1本の記事・PDF・メモ・1時点の株価スナップショット等）のみこのスキルで扱う。

## 手順

1. `type` を確認する: `web_article` / `memo` / `pdf` / `youtube` / `image` / `disclosure` / `market_data` / `link`
2. `type` に応じて内容を確認する:
   - `web_article` / `youtube` / `disclosure` / `link` → `url` が必須
   - `memo` → 本文（`body`）が必須
3. `evidenceTier` を必ず選ばせる（省略不可）:
   - `primary_disclosure`: 適時開示・決算短信・有価証券報告書などの一次情報
   - `company_issued`: IR説明会資料・広報発表など企業発信
   - `third_party`: 業界紙・競合・顧客・アナリストレポートなど第三者
   - `inference`: 一次情報からの推論・推測（裏付けが弱いもの）
4. `url` 等が与えられた対象について、内容を取得できる場合は読み取り、`domain/data/finding.md#保存フォーマット大方針` の「本文に書くべきこと/書かないこと」に従って Markdown 本文を整理する（見出し・引用を活用し、個人の感想・解釈は書かない。取得に失敗した場合は「取得に失敗した旨」と判明している情報のみを本文に記す）。`memo` の場合は入力本文をそのまま使う。
5. UUID を生成する: `uuidgen`
6. 以下を実行する:
   ```
   uv run python scripts/findings.py add --id <uuid生成結果> --type "<type>" \
     --title "<title>" --evidence-tier "<evidenceTier>" \
     [--url "<url>"] [--source-url "<sourceUrl>"] [--body "<整理した本文>"] \
     [--content-updated-at "<ISO8601>"] [--tags "tag1,tag2"]
   ```
7. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝え、再入力を促す。よくある失敗:
   - `title` が空
   - `type` に応じた必須項目（`url`/`body`）が空
   - 同一 `url` の Finding が既に登録済み
8. 成功時は stdout の JSON をもとに登録完了を伝える。
9. **必ず**、この Finding に対する Thought の追加を投資家に促す（`add-thought` skill）。少なくとも1つの Thought を付与するまでこの Finding は「未整理」の状態である。

## 注意

- `data/vault/findings/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
- Finding 自体は Company/Sector/Theme への関連を持たない。関連付けはすべて `add-thought` skill（Thought）が担う。
