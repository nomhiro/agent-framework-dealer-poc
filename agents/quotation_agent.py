import os
import json
from typing import List, Optional, Any
from schemas.quotation_schema import QuotationAgentResponse
from tools.mcp_tools import MCPToolClient

try:
    from agent_framework import MCPStreamableHTTPTool
    from agent_framework.azure import AzureAIAgentClient
except ImportError:  # pragma: no cover
    MCPStreamableHTTPTool = None  # type: ignore
    AzureAIAgentClient = None  # type: ignore

FRAMEWORK_MODE_ENV = "AGENT_FRAMEWORK_MODE"


# Note: previous loan-oriented _build_instructions was removed because QuotationAgent now
# calculates subscription monthly fees. The framework path composes its own subscription
# instructions inline to avoid stale loan-related wording.


class QuotationAgent:
    """Dual-mode QuotationAgent (procedural default / framework optional)."""

    def __init__(
        self,
        mcp: Optional[MCPToolClient] = None,
        framework_client: Optional[Any] = None,
        mcp_url: Optional[str] = None,
    ):
        self.mcp = mcp
        self.framework_client = framework_client
        self.mcp_url = mcp_url or os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")

    async def _run_procedural(
        self,
        engine_id: Optional[str] = None,
        vehicle_price: Optional[float] = None,
        subscription_term_months: Optional[int] = None,
        included_mileage_per_month: Optional[float] = None,
        maintenance_included: Optional[bool] = None,
        discount_percent: Optional[float] = None,
    ) -> QuotationAgentResponse:
        payload = {
            "engine_id": engine_id,
            "vehicle_price": vehicle_price,
            "subscription_term_months": subscription_term_months or 36,
            "included_mileage_per_month": included_mileage_per_month,
            "maintenance_included": maintenance_included,
            "discount_percent": discount_percent,
        }
        res = await self.mcp.call_tool("QuotationCalculator", payload)  # type: ignore
        # Map mock/tool response to QuotationAgentResponse
        monthly_fee = res.get("monthly_fee")
        breakdown = res.get("breakdown", {})
        term = res.get("subscription_term_months", payload["subscription_term_months"])
        total_cost = res.get("total_cost", monthly_fee * term if monthly_fee else 0)
        rationale = res.get("rationale", [])
        return QuotationAgentResponse(
            engine_id=res.get("engine_id") or engine_id,
            vehicle_price=res.get("vehicle_price") or vehicle_price,
            subscription_term_months=term,
            monthly_fee=monthly_fee or 0.0,
            breakdown=breakdown,
            total_cost=total_cost,
            rationale=rationale,
            metadata={"version": "1.0.0"},
        )

    async def _run_framework(
        self,
        engine_id: Optional[str] = None,
        vehicle_price: Optional[float] = None,
        subscription_term_months: Optional[int] = None,
        included_mileage_per_month: Optional[float] = None,
        maintenance_included: Optional[bool] = None,
        discount_percent: Optional[float] = None,
    ) -> QuotationAgentResponse:
        """Framework (LLM + tool) path with structured output enforcement.

        Strategy:
          1. Try create_agent with response_format=QuotationAgentResponse (if supported by this agent-framework version).
          2. Run once; call try_parse_value(). If value missing, re-ask with repair prompt.
          3. If still missing, attempt JSON substring extraction; if fail -> fallback skeleton.
        """
        if AzureAIAgentClient is None or MCPStreamableHTTPTool is None:
            raise RuntimeError("agent-framework not available; install dependency or unset AGENT_FRAMEWORK_MODE")
        if self.framework_client is None:
            raise RuntimeError("framework_client not provided for framework mode")

        # adapt instructions for subscription calculator
        instructions = (
            "あなたは QuotationAgent（サブスク月額計算）です。QuotationCalculator ツールを一度だけ呼び、"
            "入力パラメータ: engine_id, vehicle_price, subscription_term_months, included_mileage_per_month, maintenance_included, discount_percent を渡してください。"
            "出力は厳格な JSON で keys: monthly_fee, breakdown, total_cost, subscription_term_months, engine_id, vehicle_price のみを含めてください。"
        )

        agent_kwargs = dict(name="QuotationAgent", instructions=instructions)
        try:
            agent = self.framework_client.create_agent(response_format=QuotationAgentResponse, **agent_kwargs)  # type: ignore[arg-type]
        except TypeError:
            # Older SDK version not supporting response_format
            agent = self.framework_client.create_agent(**agent_kwargs)

        thread = agent.get_new_thread()
        user_prompt = (
            f"対象エンジン: {engine_id or 'unspecified'}\n車両価格: {vehicle_price or 'unspecified'}\n"
            f"契約期間(月): {subscription_term_months or 36}\n含まれる月間走行距離: {included_mileage_per_month or 'unspecified'}\n"
            f"メンテ込み: {maintenance_included}\n割引(%): {discount_percent or 0}\n"
            "上記情報を基にサブスク月額 monthly_fee と breakdown、total_cost を持つ JSON を出力してください。"
        )
        async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
            result = await agent.run(user_prompt, thread=thread, store=True, tools=mcp_server)

        # Primary structured parse
        try:
            # Chat/AgentRun response API: try_parse_value sets .value if parse OK
            result.try_parse_value(output_format_type=QuotationAgentResponse)  # type: ignore[attr-defined]
        except Exception:
            pass

        # Retry if missing structured value
        if not getattr(result, "value", None):
            repair_prompt = (
                "前回出力はスキーマ不一致です。monthly_fee, breakdown, total_cost, subscription_term_months, engine_id, vehicle_price を含む有効 JSON を出力してください。"
            )
            async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
                result2 = await agent.run(repair_prompt, thread=thread, store=True, tools=mcp_server)
            try:
                result2.try_parse_value(output_format_type=QuotationAgentResponse)  # type: ignore[attr-defined]
            except Exception:
                pass
            if getattr(result2, "value", None):
                result = result2

        if getattr(result, "value", None):  # Pydantic model instance
            return result.value  # type: ignore[return-value]

    # Fallback: substring JSON extraction
        txt = str(result)
        extracted = None
        if "{" in txt and "}" in txt:
            st = txt.find("{")
            ed = txt.rfind("}") + 1
            try:
                extracted = json.loads(txt[st:ed])
            except Exception:
                extracted = None
        if extracted:
            try:
                return QuotationAgentResponse(**extracted)
            except Exception:
                pass

        # Final fallback skeleton
        try:
            fallback = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        except Exception:
            fallback = {}
        return QuotationAgentResponse(
            engine_id=fallback.get("engine_id"),
            vehicle_price=fallback.get("vehicle_price"),
            subscription_term_months=fallback.get("subscription_term_months", subscription_term_months or 36),
            monthly_fee=fallback.get("monthly_fee", 0.0),
            breakdown=fallback.get("breakdown", {}),
            total_cost=fallback.get("total_cost", 0.0),
            rationale=["構造化失敗"],
            metadata={"version": "1.0.0", "raw_output": txt},
        )

    async def run(
        self,
        engine_id: Optional[str] = None,
        vehicle_price: Optional[float] = None,
        subscription_term_months: Optional[int] = None,
        included_mileage_per_month: Optional[float] = None,
        maintenance_included: Optional[bool] = None,
        discount_percent: Optional[float] = None,
    ) -> QuotationAgentResponse:
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode == "framework":
            return await self._run_framework(engine_id, vehicle_price, subscription_term_months, included_mileage_per_month, maintenance_included, discount_percent)
        if not self.mcp:
            raise RuntimeError("Procedural mode requires MCPToolClient instance")
        return await self._run_procedural(engine_id, vehicle_price, subscription_term_months, included_mileage_per_month, maintenance_included, discount_percent)
