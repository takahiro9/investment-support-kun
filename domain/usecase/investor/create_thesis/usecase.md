# 投資仮説を組み立てる (Create Thesis)

## 目的・概要

投資家が、蓄積された複数の `Thought`（意味づけ）を束ね、1つの `Company` についての投資仮説（`Thesis`）へ収斂させる。裸の Finding や単一の Thought はスタンスを持たないため、Thesis は複数の Thought を根拠として積み上げて初めて成立する。

Thesis の核心は、市場の織り込み（コンセンサス比較）を必須で明文化することにある。企業の未来予測が正しくても、それが既に株価に織り込まれていればリターンはゼロになる。そのため、市場は今どう見ているか（`consensusView`）、自分の見立てはどこがどうズレているか（`variant`）、なぜ市場がまだ気づいていないと言えるか（`whyMispriced`）を必ず言語化する。あわせて、何が起きたら仮説が崩れるか（`invalidation`）、何が起きたら確度が上がるか（`confirmation`）も対で必ず記述する。

## 事前条件

- 対象となる `Company` が存在すること
- 束ねる対象となる `Thought` が1つ以上存在すること（0件から Thesis は作れない）

## 事後条件

- 新しい `Thesis` が `status = seed` でシステムに保存されること

## 基本フロー（正常系）

1. 投資家は、対象の `Company` を選択し、仮説を一言で表す見出し（`statement`）を入力する。
2. 投資家は、この仮説の根拠とする `Thought` を1つ以上選択する（`thoughtIds`）。
3. 投資家は、以下を必須項目としてすべて記述する:
   - `consensusView`（市場は今どう見ているか）
   - `variant`（自分の見立てはどこがどうズレているか）
   - `whyMispriced`（なぜ市場がまだ気づいていない/織り込めていないと言えるか）
   - `invalidation`（何が起きたら崩れるか、反証条件）
   - `confirmation`（何が起きたら確度が上がるか、確証条件）
   - `body`（論証本文。なぜこの Thought 群からこの statement が立つのか）
4. 投資家は、任意で `horizon`（時間軸の目安）と `probability`（確度の目安）を入力する。
5. システムは、`statement`/`consensusView`/`variant`/`whyMispriced`/`invalidation`/`confirmation`/`body` がいずれも空文字列でないことを検証する。
6. システムは、新しい `Thesis` エンティティを `status = seed` として作成し、保存する。
7. システムは、作成完了を投資家に通知し、作成された Thesis の詳細画面（[View Thesis](../view_thesis/usecase.md)）へ遷移させる。

## 代替フロー・例外フロー

- **3a. 必須項目のいずれかが空の場合:**
  システムは保存処理を行わず、未入力の項目を明示してエラーを返す。とくに `consensusView` / `variant` / `whyMispriced` が埋まらない場合は「まだ Thesis として言語化できる段階ではない」ことを示すメッセージを添える。
- **2a. 束ねる Thought がまだ十分でないと投資家が感じる場合:**
  投資家はこの画面から Company の詳細（[View Company](../view_company/usecase.md)）に戻り、ドライバーツリーの空白ノードを埋めるための Finding / Thought 追加を先に行える。

## 関連するドメインモデル

- [Thesis](../../../data/thesis.md)
- [Thought](../../../data/thought.md)
- [Company](../../../data/company.md)
