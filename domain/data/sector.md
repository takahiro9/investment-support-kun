# Sector — 業種

## 概要

Companyが属する業種の軽量なマスタエンティティ。セクターは今後も増え続ける前提に立ち、Phase 1の時点で（Companyの自由記述属性としてではなく）独立エンティティとして導入する。理由: 後からCompanyの文字列属性を正規化されたエンティティへ移行するコストが高いため。

Sectorは主に2つの役割を持つ。

- **Companyの分類軸**: 同一Sectorに属する複数のCompanyを相対比較できるようにする（パイロットは「同一セクター内3〜5社」を単位とする）
- **ドライバーツリーのテンプレート単位**: 業種ごとに事業構造の分解（売上・利益・競争ポジションの分解軸）は異なるため、Sector単位でテンプレートを持ち、Companyはこれをコピーして個別化する

新しいセクターへの拡張は「Sectorを1件追加し、ドライバーツリーテンプレートを用意し、Companyを紐づける」という定型作業として繰り返せる設計にする。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `name` | string | ✅ | セクター名（例: "半導体製造装置"） |
| `driverTreeTemplate` | `DriverTreeNode[]` | ❌ | ドライバーツリーの骨格テンプレート。新規Companyはこれをコピーして個別化する。空配列（未定義）で始めてもよい |
| `createdAt` | datetime | ✅ | 作成日時 |

`DriverTreeNode` の定義は [Company](company.md#driver-tree-node) を参照（CompanyとSectorで同じ構造を共有する）。

---

## 不変条件・ビジネスルール

- `name` は空文字列にできない。システム全体で一意（同名セクターの重複登録は不可）
- `driverTreeTemplate` は未設定（空配列）でもSectorを作成できる。後から充実させてよい
- `driverTreeTemplate` を更新しても、既存Companyの `driverTree`（コピー後に個別化されたもの）には自動反映されない（テンプレートはコピー元であり、以後の同期はしない）

---

## 他ドメインオブジェクトとの関係

- **Company** — Sectorは複数のCompanyを持ち、Companyも複数のSectorに属してよい（多対多）。Companyは`sectorIds`（実質的な事業を持つSector群）と`primarySectorId`（ヘッドライン分類、ドライバーツリーの初期テンプレート用）でSectorを参照する。1つの企業が複数事業を持つ場合（例: 食品企業が半導体材料事業も持つ）を表現するための設計
- **Source** — 業界レイヤーのSourceは特定のSectorに紐づく（`layer=sector`の場合、`sectorId`を持つ）
- **Thought** — SectorレベルのFindingへの意味づけは、Thoughtの`sectorIds`を介して行う
- **[Theme](theme.md)** — Phase 4で導入。複数Sectorを跨ぐマクロ・業界動向はThemeとして括り、Sector×Themeの多対多で紐づける

---

## 保存フォーマット（大方針）

Sectorは `data/vault/sectors/<id>.md` に YAML フロントマター（属性一覧のみ、本文は基本的に使わない）として保存する。業種の背景説明を書き残したい場合は本文（Markdown、任意）に自由に記述してよい。
