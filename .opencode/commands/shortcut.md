---
description: Shortcut フォルダにアプリケーション・OS操作ノートを作成
agent: build
---

# /shortcut - Shortcut ノート作成

Shortcut フォルダにアプリケーション・OS 操作に関するノートを作成します。

引数（トピック）: $ARGUMENTS

## 使用方法

```
/shortcut chrome
/shortcut tmux
/shortcut windows
```

## 実行フロー（段階的に実行）

### Step 1: トピックの受け取り

引数 $ARGUMENTS を確認する。空の場合は「何のノートを作成したいか」をユーザーに確認して停止する。

### Step 2: 規約の読み込み

以下のルールファイルを必ず読み込んでから本文作成に進む。

@.opencode/rules/shortcut-notes.md

### Step 3: 現在時刻の取得

シェルで以下を実行し、出力をそのまま `created` と `modified` の値に使う：

```bash
date '+%Y-%m-%d %H:%M:%S'
```

### Step 4: タグの決定

`tags` には **必ず以下** を含める：

1. `shortcut`
2. アプリケーション名（chrome, terminal, windows, vim など）

例: `[shortcut, chrome]`

### Step 5: ノートの作成

`Shortcut/<topic>.md` を作成。フロントマターは以下のテンプレートに従う：

```yaml
---
title: "<トピック名>"
author: holly
tags:
  - shortcut
  - <アプリ名>
created: <Step 3 の date 出力>
modified: <Step 3 の date 出力>
---
```

本文は最低限以下のセクションを含む：

- `## 概要` - ツール・アプリケーションの説明
- `## インストール / セットアップ` - インストール手順
- `## 基本操作` - 基本的な使い方
- `## キーバインド / ショートカット` - よく使うコマンド・キーバインド表
- `## 設定` - 設定方法
- `## よくある操作` - 実用的な Tips

### Step 6: 編集完了で停止

ノート作成が完了したら、ユーザーに保存先パスを報告して停止する。git 操作は `/git-publish` まで実行しない。

## 適用ルール（参照）

@.opencode/rules/shortcut-notes.md
