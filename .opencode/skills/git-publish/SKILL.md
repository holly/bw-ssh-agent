---
name: git-publish
description: git ワークフロー（add → commit → push）
---

# git-publish

git ワークフロー。

## 使用タイミング

- **ファイル編集・作成時**: Claude はファイル変更を完了させ、git 操作なしで**一度停止**
- **確認後に呼び出し**: ユーザーが変更内容を確認してから `/git-publish` を実行するか、`commit/push して` と依頼
- **分離の理由**: ユーザーが git push 前に変更を確認したいケースがあるため

## 実行フロー

### 1. ファイルをステージ

```bash
git add <対象ファイル>
```

指定したファイルのみをステージに追加する。`git add .` や `git add -A` は使わない。

### 2. ステータス確認

```bash
git status
```

ステージされたファイルを確認。意図しないファイルが含まれていないか確認する。

### 3. コミット（Conventional Commits 形式）

```bash
git commit -m "feat: <説明>"
```

コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/ja/) 形式で作成。

### 4. リモートにプッシュ

```bash
git push origin $(git rev-parse --abbrev-ref HEAD)
```

現在のブランチ名を自動判定してプッシュ。

## ワークフロー全体

```bash
# ファイルをステージ
git add English/新しいノート.md

# ステータス確認
git status

# コミット
git commit -m "docs: Add new English note about X"

# プッシュ
git push origin $(git rev-parse --abbrev-ref HEAD)
```

## 注意事項

- コミットメッセージは簡潔に（1行目で内容が伝わるように）
- 複数のノートを同時に作成した場合、まとめて1コミットで OK
