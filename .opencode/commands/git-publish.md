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

### 5. バージョン整合性確認（push 前必須）

```bash
PYPROJECT_VERSION=$(grep '^version' pyproject.toml | sed 's/.*= *"\(.*\)".*/\1/')
SCRIPT_VERSION=$(grep '^VERSION = ' bw-ssh-agent.py | sed 's/.*"\(.*\)".*/\1/')

if [ "$PYPROJECT_VERSION" != "$SCRIPT_VERSION" ]; then
    echo "❌ バージョン不一致: push を中止します" >&2
    echo "   pyproject.toml : $PYPROJECT_VERSION" >&2
    echo "   bw-ssh-agent.py: $SCRIPT_VERSION" >&2
    echo "   両者を一致させてから再度 /git-publish を実行してください。" >&2
    exit 1
fi
```

### 6. タグ自動判定＆付与

```bash
LATEST_TAG=$(git tag -l 'v*' | sed 's/^v//' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ] || \
   ([ "$PYPROJECT_VERSION" != "$LATEST_TAG" ] && \
    [ "$(printf '%s\n%s\n' "$LATEST_TAG" "$PYPROJECT_VERSION" | sort -V | tail -1)" = "$PYPROJECT_VERSION" ]); then
    git tag -a "v$PYPROJECT_VERSION" -m "Release v$PYPROJECT_VERSION"
    echo "🏷️ タグ v$PYPROJECT_VERSION を作成しました"
fi
```

### 7. リモートにプッシュ

```bash
git push origin $(git rev-parse --abbrev-ref HEAD) --follow-tags
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
