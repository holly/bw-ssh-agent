---
description: リモートから最新変更を取得
agent: build
---

# git-pull

リモートリポジトリから最新の変更を取得する。

## 実行フロー

### 1. 現在のブランチを確認

```bash
git branch
```

作業中のブランチを確認する。

### 2. リモートから pull

```bash
git pull --ff-only origin $(git rev-parse --abbrev-ref HEAD)
```

現在のブランチを自動判定し、fast-forward のみで最新変更を取得する。

### 3. 結果を通知

## 出力パターン

### 成功時

```
✅ 最新状態に更新しました。
Already up to date.
(または)
X files changed, Y insertions(+), Z deletions(-)
```

### 既に最新の場合

```
✅ すでに最新状態です。
Already up to date.
```

### 競合が発生した場合

```
❌ 競合が発生しました。--ff-only フラグのため pull を中止しました。

以下の操作が必要です：
1. git fetch origin <ブランチ名> で最新をダウンロード
2. 手動で競合を解決
3. git merge origin/<ブランチ名> または git rebase origin/<ブランチ名> で統合

または別端末での変更を確認して、手動で統合してください。
```

## フラグ説明

- `--ff-only`: fast-forward のみ許可
  - マージコミットが必要な場合（競合がある場合）は中止
  - 意図しないマージを防ぐため

## 使用タイミング

- `/git-pull` コマンドで明示的に実行したい場合
