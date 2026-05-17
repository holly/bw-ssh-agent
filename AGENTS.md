# AGENTS.md

## プロジェクト概要

- `bw-ssh-agent.py` は、Bitwarden Vault に保存されたSSH秘密鍵を自動で読み出し、`ssh-agent` に登録するユーティリティスクリプトです。
- シェルの環境変数（`SSH_AUTH_SOCK`, `SSH_AGENT_PID`）を適切に設定・出力し、シームレスなSSH認証エージェント管理を提供します。

## 技術スタック

- Python 3
- bash / zsh / fish（シェル連携）

## 実行方法

- 必ず `uv` を使用してください
- 実行例: `uv run python bw-ssh-agent.py [bash|zsh|fish]`

## エントリポイント

- `bw-ssh-agent.py`（単一ファイル）

## 外部依存・実行時コマンド

- `bw` (Bitwarden CLI)
- `ssh-agent`
- `ssh-add`
- `pgrep`
- 環境変数 `BW_SESSION` が必要（`bw unlock --raw` で取得）

## プロジェクト構造

```
bw-ssh-agent/
├── bw-ssh-agent.py    # メインスクリプト
├── README.md
├── LICENSE
├── pyproject.toml     # uv 用設定
├── uv.lock
├── .python-version
├── .gitignore
└── .venv/             # uv 仮想環境
```

## 禁止事項

以下の操作は**禁止**：

- ファイル・ディレクトリの**削除**

## 言語

応答は常に**日本語**を使用する。

# 共通ルール

## モデル非依存の指示遵守

このプロジェクトは Anthropic・OpenAI・Google・ローカルモデル（Ollama 等）を含む複数モデルでの動作を想定しています。以下を厳守してください：

1. **段階的に実行する**: 各コマンドの「実行フロー」を番号順に必ず守り、各段階で完了確認してから次に進む
2. **暗黙の判断を避ける**: 「適切に」「自然に」のような曖昧な指示は無視し、明示的に書かれた判定表・条件のみに従う
3. **静的な値を出力する**: フロントマターの日時・タグはコマンドの出力結果をそのまま使い、推測・補完しない
4. **モデル固有構文を使わない**: XML タグ（`<thinking>` 等）、Anthropic 固有のメタ構文は出力に含めない。Markdown のみで記述する


## 注意事項

- 本スクリプトは Bitwarden Vault にアクセスするため、事前にセッションがロック解除されている必要があります。
- 既存の ssh-agent プロセスが存在する場合、エラーで終了します。
