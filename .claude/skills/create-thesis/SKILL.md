---
name: create-thesis
description: Bundle accumulated Thoughts into a single investment Thesis for a Company — consensus view, variant, why-mispriced, invalidation/confirmation conditions. Use when the investor is ready to commit to a testable investment hypothesis, not just scattered observations.
---

# 投資仮説を組み立てる (Create Thesis)

Spec: `domain/usecase/investor/create_thesis/usecase.md`, `domain/usecase/investor/create_thesis/tech_context.md`

## 事前条件

対象 `Company` が存在し、束ねる根拠となる `Thought` が1つ以上存在すること。まだ Thought が薄いと投資家が感じる場合は、先に `view-company` skill でドライバーツリーの空白ノードを確認し、`add-finding`/`add-thought` で埋めることを提案する。

## 手順

1. 対象 `Company` の id を確認する（分からなければ `list-companies` skill）。
2. 仮説の見出し（`statement`）を確認する。
3. この仮説の根拠とする `Thought` を1つ以上選んでもらう（`thoughtIds`）。分からなければ `view-company` skill でその Company に紐づく Finding/Thought を辿る。
4. 以下を **すべて空文字列不可** として確認する:
   - `consensusView`（市場は今どう見ているか）
   - `variant`（自分の見立てはどこがどうズレているか）
   - `whyMispriced`（なぜ市場がまだ気づいていない/織り込めていないと言えるか）
   - `invalidation`（何が起きたら崩れるか、反証条件）
   - `confirmation`（何が起きたら確度が上がるか、確証条件）
   - `body`（論証本文。なぜこの Thought 群から `statement` が立つのか）
5. 任意で `horizon`（時間軸の目安、日付）と `probability`（0〜1の確度の目安）を確認する。
6. UUID を生成する: `uuidgen`
7. 以下を実行する:
   ```
   uv run python scripts/theses.py register --id <uuid生成結果> --company-id "<companyId>" \
     --statement "<statement>" --consensus-view "<consensusView>" --variant "<variant>" \
     --why-mispriced "<whyMispriced>" --invalidation "<invalidation>" --confirmation "<confirmation>" \
     --thought-ids "<id1>,<id2>" --body "<論証本文>" \
     [--horizon "<YYYY-MM-DD>"] [--probability <0-1>] [--tags "tag1,tag2"]
   ```
8. コマンドが非ゼロで終了した場合、stderr の `{"errors": [...]}` を伝える。よくある失敗:
   - 必須項目のいずれかが空（とくに `consensusView`/`variant`/`whyMispriced` が埋まらない場合は「まだ Thesis として言語化できる段階ではない」ことを伝える）
   - `thoughtIds` が空、重複、または存在しない Thought を含む
   - `companyId` が存在しない
9. 成功時は stdout の JSON をもとに登録完了を伝える。`status` は常に `seed` から始まることを伝え、`view-thesis`/`update-thesis-status` skill への導線を示す。

## 注意

`data/vault/theses/` の md ファイルを直接編集・作成してはならない。必ずこのスクリプト経由で行う。
