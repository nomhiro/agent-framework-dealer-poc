# Agent Framework PoC (ProposalAgent)

このリポジトリは Microsoft Agent Framework を利用した販売店向け PoC サンプルです。

## Setup

依存追加 (pre-release を利用):

```powershell
uv add agent-framework --pre
uv add azure-identity
```

## Environment (.env) and Local run (az login を利用)

このリポジトリは `.env` ファイルを使った環境変数設定を想定しています。ローカル実行では `az login` による Azure CLI 認証を前提とします。

1. 仮想環境の作成と有効化 (PowerShell):

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    ```

2. 依存のインストール（`uv` を使うか pip）:

    ```powershell
    uv sync  # uv を使って依存をインストールしている場合
    # または
    pip install --pre agent-framework
    pip install azure-identity
    ```

3. `.env` ファイル作成（ルートに置く） - 必須項目の例:

    ```env
    AZURE_AI_PROJECT_ENDPOINT="https://your-project-endpoint"
    AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
    # Optional: Bing grounding
    BING_CONNECTION_ID="/subscriptions/.../resourceGroups/.../providers/.../connections/..."
    # If using local MCP server (functions-mcp):
    MCP_SERVER_URL="http://localhost:7071/api/mcp"
    ```

    > 注: サンプルは `.env.example` を参照する形になっている場合があります。プロジェクトルートに `.env` を配置してください。

4. Azure CLI にログイン（ローカル開発で AzureCliCredential を使う場合）:

    ```powershell
    az login
    az account show
    ```

5. (オプション) Azure Service Principal を使う場合（CI 等）:

    ```powershell
    $env:AZURE_CLIENT_ID = "..."
    $env:AZURE_TENANT_ID = "..."
    $env:AZURE_CLIENT_SECRET = "..."
    ```

## Run ProposalAgent (Minimal)

1. （必要あれば）別ターミナルで Azure Functions (functions-mcp) を起動（`func start`、想定ポート 7071）
2. ProposalAgent を実行:

    ```powershell
    python proposal_agent.py --query "家族4人 ハイブリッド 納期短め 予算400万" --priority lead_time --auto-approve
    ```

出力は JSON 構造 (recommendations / normalized_requirements / metadata) を返します。ツール接続が失敗する場合は `MCP_SERVER_URL` の値を `.env` で調整してください。

## Run Orchestrator REPL (Multi-turn chat)

framework モードで orchestrator を使った対話型 REPL を起動できます:

```powershell
$env:AGENT_FRAMEWORK_MODE="framework"
python .\orchestrator_chat_repl.py --query "SUVかハッチバック" --priority balance --fuel-pref hybrid
```

### ログ・デバッグオプション

詳細ログを有効にしてツール呼び出しや応答を確認:

```powershell
# コンソールに詳細ログを出力（DEBUG レベル）
python .\orchestrator_chat_repl.py --query "SUV 400万 4名" --verbose

# ログをファイルに保存
python .\orchestrator_chat_repl.py --query "SUV 400万 4名" --verbose --log-file orchestrator.log

# OpenTelemetry トレースを有効化（Application Insights 連携時）
python .\orchestrator_chat_repl.py --query "SUV 400万 4名" --enable-otel
```

ログには以下が含まれます:
- ユーザー入力とクエリパラメータ
- ツール呼び出し（call_proposal, call_quotation, call_finance）の引数と結果
- LLM 応答の machine_output 構造
- エラー詳細（ValidationError 等）

### REPL コマンド

- `/json` — 最新の machine_output (JSON) を表示
- `/reset` — 会話を完全リセット（新しいクエリ入力を求められます）
- `/exit` — 終了
