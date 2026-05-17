---
name: git-pull
description: 最新変更を codeberg から取得
---

# git-pull

Codeberg から最新の Vault 変更を取得します。

## 実行フロー

1. **現在のブランチを確認**
   ```bash
   git branch
   ```

2. **リモートから pull**
   ```bash
   git pull --ff-only origin main
   ```

3. **結果を日本語で通知**

## 出力パターン

### 成功時

```
✅ 最新状態に更新しました。
Already up to date. (または) X files changed, Y insertions(+), Z deletions(-)
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
1. git fetch origin main で最新をダウンロード
2. 手動で競合を解決
3. git merge origin/main または git rebase origin/main で統合

または別端末での変更を確認して、手動で統合してください。
```

## フラグ説明

- `--ff-only`：fast-forward のみ許可
  - マージコミットが必要な場合（競合がある場合）は中止
  - 意図しないマージを防ぐため

## 自動実行

セッション開始時（最初のプロンプト送信時）に自動的に実行されます。
`.claude/settings.json` の `UserPromptSubmit` hook で設定。

## 使用タイミング

- **自動実行**： opencode セッション開始時
- **手動実行**：`/git-pull` コマンドで明示的に実行したい場合
