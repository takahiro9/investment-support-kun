# Changelog

このプロジェクトの変更履歴。各エントリは一言で。詳細な経緯・理由はコミットメッセージを参照。

## Unreleased

- `docker compose up`でWeb UI（claude/webappサービス）が起動するDocker構成を追加
- 企業追加フォームをプロンプト送信の中継からClaude Codeセッションの直接ptyコンソール埋め込みに変更
- Web UIのClaude Codeセッションパネルを、常時表示の右サイドバーからモーダル表示に変更した
- Web UIに企業一覧画面を追加した
- Web UIから起動するClaude Codeセッションのデフォルト権限モードを`auto`にした
- Company未登録時もWeb UIのセッションパネルから全社共通のClaude Codeセッションを開けるようにし、企業を追加できるようにした
- Companyが直接持っていた`driverTree`/`currentSnapshot`をBusiness（事業）エンティティへ切り出し、Thesisに任意の`businessId`を追加
- Thesisから`consensusView`/`variant`/`whyMispriced`を廃止し、Source/Signal/Findingのmarket区分（株価・バリュエーション・アナリストコンセンサス）を削除
- StrategyRecommendationから`pricedIn`（市場の織り込み度）を廃止
- ドメインの主目的を「投資判断支援」から「企業の意思決定構造の理解」へ再定義し、Thesis/StrategyRecommendationの必須項目を段階化
- コードレビュー指摘3件を修正（horizon検証・index部分更新の欠落・resolution-contextのtraceback）
- Thesis/Signal/Theme/StrategyRecommendation/InvestmentAction/Predictionを実装
- Source/Finding/Thought CRUDとCompany view/snapshot skillsを実装
- Vault I/O、LanceDBインデックス、Sector/Company CRUDの基盤を構築
