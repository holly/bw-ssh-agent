---
description: git ワークフロー（add → commit → push）
agent: build
---

# git-publish

git-publish skill に基づいて git の操作を行い、リポジトリへの push を行う。

## 実行フロー

### 1. 変更ファイルを確認

```bash
git status
git diff --name-only
```

変更のあるファイルを特定する。意図しないファイルが含まれていないか確認する。

### 2. ファイルをステージ

```bash
git add <対象ファイル>
```

**注意**: `git add .` や `git add -A` は使わない。変更のあったファイルのみを個別にステージに追加する。

### 3. ステージ再確認

```bash
git status
```

ステージされたファイルを確認。誤ってステージされていないか最終チェックする。

### 4. コミット（Conventional Commits 形式）

```bash
git commit -m "<type>: <説明>"
```

コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/ja/) 形式で作成する。

主な type：

- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメントのみの変更
- `style:` フォーマット（セミコロン、空白など）
- `refactor:` リファクタリング
- `test:` テストの追加・修正
- `chore:` ビルドプロセスや補助ツールの変更

### 5. リモートにプッシュ

```bash
git push origin $(git rev-parse --abbrev-ref HEAD)
```

現在のブランチ名を自動判定してプッシュする。

## エラーハンドリング

### 変更がない場合

```
変更されたファイルがありません。コミットするものがありません。
```

### プッシュ失敗時

```
❌ プッシュに失敗しました。

エラー内容を確認し、以下を試行してください：
1. git fetch origin でリモートの最新状態を確認
2. 競合があれば手動で解決
3. 再度 /git-publish を実行
```

## 使用タイミング

- ファイル編集・作成後、リモートリポジトリに反映したい場合
- `/git-publish` コマンドで明示的に実行

## 注意事項

- コミットメッセージは簡潔に（1行目で内容が伝わるように）
- 複数のファイルを同時に変更した場合、まとめて1コミットで OK
