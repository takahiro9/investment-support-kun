# Theme — 業界・マクロ動向の括り

## 概要

Phase 4で導入。単一のSectorに閉じない、複数Sectorを横断して影響する業界動向・政策・社会動向の括り。1つの政策ニュースが複数銘柄のThesisに影響しうるが、そのFinding/SourceをどのSectorにも単独で紐づけると、Sector間での再利用が表現できない。Themeを導入し、Sourceの`layer=theme`としてThemeに直接紐づけることで、複数Sectorへの横断的な影響を1つのSource/Findingの束として扱えるようにする。

Sector自体はPhase 1で先出しして導入済みのため、Phase 4で新たに必要になるのはこのThemeと、複数Sectorへの横展開のみ。

---

## 属性一覧

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string (UUID) | ✅ | 一意識別子 |
| `name` | string | ✅ | テーマ名（例: "半導体サプライチェーン再編"） |
| `description` | string | ❌ | 補足説明 |
| `sectorIds` | string[] (FK) | ❌ | このテーマが影響するSector群。全業種に影響する場合は空配列のままでよい |
| `createdAt` | datetime | ✅ | 作成日時 |

---

## 不変条件・ビジネスルール

- `name` は空文字列にできない
- `sectorIds` は0個以上。空配列は「特定のSectorに限定されない、より広いマクロ動向」を表す
- `sectorIds` の要素に重複は持たない

---

## 他ドメインオブジェクトとの関係

- **[Sector](sector.md)** — Themeは複数のSectorに影響してよい（多対多、`sectorIds`）
- **[Source](source.md)** — `layer=theme` のSourceはThemeに紐づく（`themeId`）
- **Thought** — ThemeレベルのFindingへの意味づけは、Thoughtの`themeIds`を介して行う

---

## 保存フォーマット（大方針）

Themeは `data/vault/themes/<id>.md` に YAML フロントマターとして保存する。本文は任意（テーマの背景説明等）。
