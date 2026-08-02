# Changelog

このプロジェクトの変更履歴。各エントリは一言で。詳細な経緯・理由はコミットメッセージを参照。

## Unreleased

- Companyが直接持っていた`driverTree`/`currentSnapshot`をBusiness（事業）エンティティへ切り出し、Thesisに任意の`businessId`を追加
- Thesisから`consensusView`/`variant`/`whyMispriced`を廃止し、Source/Signal/Findingのmarket区分（株価・バリュエーション・アナリストコンセンサス）を削除
- StrategyRecommendationから`pricedIn`（市場の織り込み度）を廃止
- ドメインの主目的を「投資判断支援」から「企業の意思決定構造の理解」へ再定義し、Thesis/StrategyRecommendationの必須項目を段階化
- コードレビュー指摘3件を修正（horizon検証・index部分更新の欠落・resolution-contextのtraceback）
- Thesis/Signal/Theme/StrategyRecommendation/InvestmentAction/Predictionを実装
- Source/Finding/Thought CRUDとCompany view/snapshot skillsを実装
- Vault I/O、LanceDBインデックス、Sector/Company CRUDの基盤を構築
