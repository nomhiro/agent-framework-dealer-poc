# functions-mcp: Dealer PoC MCP ツール群 (最新ドキュメント)

このフォルダーは、自動車ディーラー業務を想定した最小 PoC として実装した MCP（Model Context Protocol）ツール群を Azure Functions (Python) でホストするものです。

要旨
- 本プロジェクトは LLM/エージェントから呼び出せる標準化ツール（納期照会、見積、与信プレチェック、予約作成等）を提供します。
- 実装は `function_app.py` にて Azure Functions の `FunctionApp` を作成し、MCP 互換の generic_trigger を用いて各ツールを公開する構成になっています。ビジネスロジックは `handlers.py` に分離されています。

主なファイル
- `function_app.py` — Azure Functions エントリポイント。MCP 用の `generic_trigger` によるツール公開と HTTP ヘルスエンドポイントを含みます。
- `handlers.py` — 各ツールの処理（車種一覧、納期、見積、与信、予約、ヘルス）。
- `sample_data.py` — サンプル在庫データ（モデル、グレード、エンジンオプション）
- `requirements.txt` — 実行時依存（`azure-functions` など）。
- `tests/` — 単体確認用スクリプト（`test_leadtime.py`, `test_finance.py`, `test_reservations.py` など）。

公開しているツール（現在の実装に基づく）

1) VehicleModels
- 目的: 購入可能な車種／グレード／エンジンオプションの一覧取得（サンプル在庫ベース）。
- 入力: なし（toolProperties は空配列）
- 出力: `vehicle_models`（model_id, model_name, grades[], engine_options[] など）

2) LeadTimeAPI
- 目的: 指定モデルの納期情報を返す。
- 入力: `model_ids` (array) — 必須
  - 実装は柔軟入力を受け付けます: Python list / JSON 文字列化された配列 / カンマ区切りの文字列 を正しく正規化します。
- 出力: `items` 配列（各 model の grades と engine_options を含む、各エンジンに `est_lead_weeks`, `plant_id`, `build_slot` 等を付与）

3) QuotationCalculator (Subscription monthly fee calculator)
- 目的: 車両をサブスクリプションで提供する際の月額料金を算出するツール（PoC）。ローンの見積ではなく、サブスク契約向けの月額/内訳を返します。
- 入力（主なフィールド）:
  - `vehicle_price` (number, 任意) — ベースとなる車両価格。`engine_id` を指定すると該当エンジンの価格を自動取得します。
  - `engine_id` (string, 任意)
  - `subscription_term_months` (number, 任意, デフォルト: 36) — サブスク契約期間（月数）
  - `included_mileage_per_month` (number, 任意) — 月当たり含まれる走行キロ数（オプションに応じた加算/減額を実装可能）
  - `maintenance_included` (bool, 任意) — メンテナンス込みの場合は月額に上乗せ
  - `discount_percent` (number, 任意) — 割引率（%）
- 出力:
  - `monthly_fee` (number) — 計算された標準月額料金（税抜または税込は実装に依る）
  - `breakdown` (object) — ベース料金、メンテナンス費用、税・手数料、割引額などの内訳
  - `total_cost` (number) — サブスク期間中の総支払額（monthly_fee * months 等の集計）

サンプル入力例:
```json
{
  "vehicle_price": 3500000,
  "subscription_term_months": 36,
  "maintenance_included": true,
  "discount_percent": 5
}
```

サンプル出力例（PoC）:
```json
{
  "monthly_fee": 59800,
  "breakdown": { "base": 55000, "maintenance": 3000, "tax": 800, "discount": -4000 },
  "total_cost": 2152800,
  "term_months": 36
}
```
-
4) FinancePrecheck
- 目的: 簡易的な与信プレチェック（PoC スコアリング）
- 入力（現在のツール仕様）: トップレベルで明示的に受け取ります（`income` と `requested_amount` を必須としている点に注意）
  - `income` (number) — 必須: 年収（円）
  - `requested_amount` (number) — 必須: 希望借入額（円）
  - 任意: `age`, `employment_status`, `existing_debt`, `dependents`
- 出力: `score` (0-100), `rating` (AAA/AA/A/B), `approved` (bool), `annual_income`, `requested_amount`。必須パラメータが欠けると日本語のエラーメッセージを返します。

5) ReservationManager
- 目的: 試乗／サービス予約の作成（PoC 実装）
- 入力（必須）:
  - `customer_id` (string) — 必須
  - `vehicle_id` (string) — 必須（後方互換性で保持）
  - `grade_id` (string) — 必須（後方互換性で保持）
  - `engine_id` (string) — 必須（推奨）
  - `preferred_times` (array) — 必須（ISO 形式の日時文字列の配列を想定）
- 実装のポイント: ハンドラ側で上記全てをランタイム検証し、不足時は `{"error":"missing_required_parameters","message":"予約に必要なパラメータが不足しています: ..."}` を返します。`preferred_times` が文字列で渡された場合は配列に変換して処理します。
- 出力: `reservation_id`, `confirmed` (bool), `scheduled_time`, `conflicts`（簡易競合チェックあり）

HTTP エンドポイント（PoC 用）
- POST /api/inventory/search — InventorySearch と同等のリクエストを受け取る。
- POST /api/leadtime/get — LeadTimeAPI
- POST /api/quotation/calc — QuotationCalculator
- POST /api/finance/precheck — FinancePrecheck
- POST /api/reservations/create — ReservationManager
- GET  /api/mcp/discover — ツールのメタデータ（簡易 discovery JSON）を返す。
- POST /api/mcp/call — 汎用ディスパッチ: { "tool": "ToolName", "input": {...} } の形でツールを呼び出すと結果が `{ "result": ... }` で返る。

MCP トリガー関数
- ドキュメントの例に倣い、`@app.generic_trigger(..., type="mcpToolTrigger", toolName="...")` を利用して各ツールを MCP トリガーとしても公開しています。
- これにより、MCP サーバやクライアントが Function を直接ツールとして呼び出せる構成を供給します（注: MCP 拡張はプレビューであり、実稼働での使用には注意が必要です）。

MCP 呼び出し形式（例）
- MCP トリガーに渡されるコンテキストは JSON 文字列で来ます。一般的な形:

```json
{
  "tool": "InventorySearch",
  "arguments": {
    "query_models": ["X-Sedan-G"],
    "customer_preferences": {"budget_max": 4000000}
  }
}
```

HTTP 汎用呼び出し（/api/mcp/call）例（PowerShell）

```powershell
$body = @{
  tool = 'InventorySearch'
  input = @{ query_models = @('X-Sedan-G'); customer_preferences = @{ budget_max = 4000000 } }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri 'http://localhost:7071/api/mcp/call' -Body $body -ContentType 'application/json'
```

レスポンス例
```json
{
  "result": {
    "candidates": [
      {"model_id":"X-Sedan-G","model_name":"2025 Sedan X Hybrid G","orderable":true,"est_lead_weeks":6,"price_estimate":3500000}
    ],
    "basis":"sample_inventory"
  }
}
```

ローカルセットアップと確認手順
1. Python 仮想環境作成（推奨）
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r functions-mcp\requirements.txt
```
2. インポートチェック
```powershell
python - <<'PY'
import importlib
try:
    importlib.import_module('azure.functions')
    print('azure.functions OK')
except Exception as e:
    print('import failed:', e)
    raise
PY
```
3. Functions Core Tools で起動（`func` がインストールされている場合）
```powershell
func start
```
4. エンドポイントを curl/Invoke-RestMethod で呼んで確認

注意点・展開メモ
- `azure-functions` は `requirements.txt` に含まれていますが、IDE の静的解析で import 解決エラーが出る場合は、ワークスペースで仮想環境が未アクティブの可能性があります。
- Microsoft の MCP 拡張は現時点でプレビュー機能です。Production 環境で使用する場合は互換性・サポートポリシーを事前に確認してください。
- より正式に MCP サーバとして統合する場合、Functions 単体にマウントする方法（ドキュメント例では FastAPI 等に組み込むパターンが示されている）と、Functions の MCP 拡張を使う方法（今回実装した `generic_trigger`）のどちらにするか設計上選定してください。

追加の改善案（推奨）
- ツール仕様を JSON Schema として `schemas/` に保存し、`/mcp/discover` で返す `input_schema`/`output_schema` を厳密化する。これによりクライアント側でバリデーションが可能になります。
- `handlers.py` に対する pytest テストを追加（happy path と null/empty 入力）
- ロギングやメトリクス（Application Insights / OpenTelemetry）を追加し、稼働時の可観測性を強化する。

連絡事項
- ここまででファイル分割と MCP トリガーの雛形（ドキュメント準拠）を入れました。次にローカルでの実行検証を私が代行して行うこともできます（仮想環境作成 → pip install → import check → func start → エンドポイントテスト）。実行を希望する場合は「実行して」と指示してください。

---
Generated: 2025-10-05
