
"""
自動車ディーラー向けMCP（Model Context Protocol）対応Azure Functions
購入可能車種一覧、納期照会、ローン見積もり、融資事前審査、予約管理の機能を提供
"""
import azure.functions as func
import json
import logging

# Azure Functions アプリケーションのインスタンスを作成（匿名認証レベル）
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# === HTTPエンドポイント ===

@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """ヘルスチェックエンドポイント"""
    return func.HttpResponse(body=json.dumps(health_status()), status_code=200, mimetype="application/json")


# === ヘルパー関数の読み込み ===

# 重複を避けるためhandlers.pyからハンドラー関数をインポート
from handlers import (
    handle_vehicle_models_get,
    handle_leadtime_get,
    handle_quotation_calc,
    handle_finance_precheck,
    handle_reservations_create,
    health_status,
)


# === MCPトリガーベースの関数 ===
# 各関数はgeneric_triggerデコレータを使用してtype="mcpToolTrigger"を指定
# トリガーはJSON文字列（context）を提供し、ツールの引数は"arguments"キーに格納される

# ツールプロパティのJSON文字列定義（Microsoft Docsの例に従いtoolPropertiesをJSONテキストで提供）
# 購入可能車種一覧取得ツールのプロパティ定義（入力パラメータなし）
_TOOL_PROPERTIES_VEHICLE_MODELS_JSON = json.dumps([])

# 納期照会ツールのプロパティ定義
_TOOL_PROPERTIES_LEADTIME_JSON = json.dumps([
    {"propertyName": "model_ids", "propertyType": "array", "description": "照会するモデルIDのリスト（必須）", "required": True}
])

# ローン見積もりツールのプロパティ定義
_TOOL_PROPERTIES_QUOTATION_JSON = json.dumps([
    {"propertyName": "vehicle_price", "propertyType": "number", "description": "車両総額（engine_idまたはgrade_idが指定されている場合は省略可）", "required": False},
    {"propertyName": "engine_id", "propertyType": "string", "description": "エンジンID（指定すると価格を自動取得、推奨）", "required": False},
    {"propertyName": "grade_id", "propertyType": "string", "description": "グレードID（後方互換性）", "required": False},
    {"propertyName": "down_payment", "propertyType": "number", "description": "頭金額", "required": False},
    {"propertyName": "terms", "propertyType": "array", "description": "返済期間（月数）", "required": False}
])

# 融資事前審査ツールのプロパティ定義
_TOOL_PROPERTIES_FINANCE_JSON = json.dumps([
    {"propertyName": "income", "propertyType": "number", "description": "顧客の年収（円）", "required": True},
    {"propertyName": "requested_amount", "propertyType": "number", "description": "希望借入額（円）", "required": True},
    {"propertyName": "age", "propertyType": "number", "description": "顧客の年齢（任意）", "required": False},
    {"propertyName": "employment_status", "propertyType": "string", "description": "雇用形態（任意、例: 正社員/派遣/自営業）", "required": False},
    {"propertyName": "existing_debt", "propertyType": "number", "description": "既存の借入残高（任意、円）", "required": False},
    {"propertyName": "dependents", "propertyType": "number", "description": "扶養人数（任意）", "required": False}
])

# 予約管理ツールのプロパティ定義
_TOOL_PROPERTIES_RESERVATION_JSON = json.dumps([
    {"propertyName": "customer_id", "propertyType": "string", "description": "顧客識別子", "required": True},
    {"propertyName": "vehicle_id", "propertyType": "string", "description": "車両識別子（後方互換性）", "required": True},
    {"propertyName": "grade_id", "propertyType": "string", "description": "グレードID（後方互換性）", "required": True},
    {"propertyName": "engine_id", "propertyType": "string", "description": "エンジンID（推奨）", "required": True},
    {"propertyName": "preferred_times", "propertyType": "array", "description": "希望予約時間（ISO形式）", "required": True}
])


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="VehicleModels",
    description="購入可能な車種一覧を取得",
    toolProperties=_TOOL_PROPERTIES_VEHICLE_MODELS_JSON,
)
def vehicle_models_get_mcp(context) -> str:
    """MCPトリガーによる購入可能車種一覧取得ツール。contextはJSON文字列"""
    try:
        content = json.loads(context)
        arguments = content.get("arguments") or {}
        result = handle_vehicle_models_get(arguments)
        return json.dumps(result)
    except Exception:
        logging.exception("vehicle_models_get_mcp 実行失敗")
        return json.dumps({"error": "internal_error"})


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="LeadTimeAPI",
    description="モデルの納期情報を取得",
    toolProperties=_TOOL_PROPERTIES_LEADTIME_JSON,
)
def leadtime_get_mcp(context) -> str:
    """MCPトリガーによる納期照会ツール"""
    try:
        content = json.loads(context)
        arguments = content.get("arguments") or {}
        result = handle_leadtime_get(arguments)
        return json.dumps(result)
    except Exception:
        logging.exception("leadtime_get_mcp 実行失敗")
        return json.dumps({"error": "internal_error"})


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="QuotationCalculator",
    description="ローンプランを計算",
    toolProperties=_TOOL_PROPERTIES_QUOTATION_JSON,
)
def quotation_calc_mcp(context) -> str:
    """MCPトリガーによるローン見積もりツール"""
    try:
        content = json.loads(context)
        arguments = content.get("arguments") or {}
        result = handle_quotation_calc(arguments)
        return json.dumps(result)
    except Exception:
        logging.exception("quotation_calc_mcp 実行失敗")
        return json.dumps({"error": "internal_error"})


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="FinancePrecheck",
    description="信用度事前審査",
    toolProperties=_TOOL_PROPERTIES_FINANCE_JSON,
)
def finance_precheck_mcp(context) -> str:
    """MCPトリガーによる融資事前審査ツール"""
    try:
        content = json.loads(context)
        arguments = content.get("arguments") or {}
        result = handle_finance_precheck(arguments)
        return json.dumps(result)
    except Exception:
        logging.exception("finance_precheck_mcp 実行失敗")
        return json.dumps({"error": "internal_error"})


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="ReservationManager",
    description="予約エントリの作成（試乗・サービス）",
    toolProperties=_TOOL_PROPERTIES_RESERVATION_JSON,
)
def reservations_create_mcp(context) -> str:
    """MCPトリガーによる予約管理ツール"""
    try:
        content = json.loads(context)
        arguments = content.get("arguments") or {}
        result = handle_reservations_create(arguments)
        return json.dumps(result)
    except Exception:
        logging.exception("reservations_create_mcp 実行失敗")
        return json.dumps({"error": "internal_error"})
