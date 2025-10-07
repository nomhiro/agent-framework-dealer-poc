import os
import json
from typing import List, Optional, Any
from datetime import datetime
from schemas.proposal_schema import (
    ProposalAgentResponse,
    ProposalQuery,
    Recommendation,
    NormalizedRequirements,
)
from tools.mcp_tools import MCPToolClient

# Optional agent-framework imports (only needed in framework mode)
try:
    from agent_framework import MCPStreamableHTTPTool, AgentProtocol, AgentThread
    from agent_framework.azure import AzureAIAgentClient
except ImportError:  # pragma: no cover
    MCPStreamableHTTPTool = None  # type: ignore
    AzureAIAgentClient = None  # type: ignore
    AgentProtocol = None  # type: ignore
    AgentThread = None  # type: ignore


FRAMEWORK_MODE_ENV = "AGENT_FRAMEWORK_MODE"  # set to "framework" to enable LLM tool-calling path


def _build_instructions(priority: Optional[str]) -> str:
    pr = priority or "balance"
    return (
        "あなたは自動車販売店の ProposalAgent です。"
        "ユーザー要求を正規化し、必要に応じて以下ツールを利用して候補を 2~3 件 JSON で出力してください。"
        "ツール: VehicleModels (必須で最初に 1 回), priority='lead_time' の場合のみ LeadTimeAPI を 1 回。"
        f" priority={pr}. 出力は厳格な JSON (recommendations[], normalized_requirements, next_action_hint, metadata) のみ。"
        " **重要**: recommendations 各項目に vehicle_price (VehicleModels の price フィールド) を必ず含めてください。"
        " recommendations[].reasons は短い根拠文の配列。日本語で簡潔に。追加の自由記述は禁止。"
    )


class ProposalAgent:
    """Dual-mode ProposalAgent.

    - procedural mode (default): Python で直接 MCP ツール呼び出し (以前のロジック)
    - framework mode: agent-framework の LLM + tool calling を使用
      有効化: env AGENT_FRAMEWORK_MODE=framework
    """

    def __init__(
        self,
        mcp: Optional[MCPToolClient] = None,
        framework_client: Optional[Any] = None,
        mcp_url: Optional[str] = None,
    ):
        self.mcp = mcp
        self.framework_client = framework_client
        self.mcp_url = mcp_url or os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")

    # ---------------- Procedural path (previous implementation) -----------------
    async def _run_procedural(self, query: ProposalQuery) -> ProposalAgentResponse:
        vm = await self.mcp.call_tool("VehicleModels", {})  # type: ignore
        models = vm.get("vehicle_models", [])

        candidates = []
        for v in models:
            if query.fuel_pref and v.get("fuel") != query.fuel_pref:
                continue
            candidates.append(v)
        if not candidates:
            candidates = models

        recs: List[Recommendation] = []
        for v in candidates[:2]:
            grade = v.get("grades", [])[0]
            engine = grade.get("engine_options", [])[0]
            recs.append(
                Recommendation(
                    model_id=v.get("model_id"),
                    grade_id=grade.get("grade_id"),
                    engine_id=engine.get("engine_id"),
                    vehicle_price=engine.get("price"),
                    reasons=["matches fuel preference" if query.fuel_pref else "general fit"],
                    est_lead_weeks=None,
                )
            )
        if query.priority == "lead_time":
            model_ids = [r.model_id for r in recs]
            lt = await self.mcp.call_tool("LeadTimeAPI", {"model_ids": model_ids})  # type: ignore
            items = lt.get("items", [])
            for r in recs:
                for it in items:
                    if it.get("model_id") == r.model_id:
                        r.est_lead_weeks = it.get("est_lead_weeks")

        normalized = NormalizedRequirements(
            budget_max=query.budget_max,
            passenger_count=query.passenger_count,
            priority=query.priority,
            fuel_pref=query.fuel_pref,
        )
        return ProposalAgentResponse(
            recommendations=recs,
            normalized_requirements=normalized,
            next_action_hint="見積詳細へ進むか、用途詳細(年間走行距離)を補足してください",
            metadata={
                "version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "source_tools": ["VehicleModels"],
            },
        )

    # ---------------- Framework path (LLM + tool calling) -----------------
    async def _run_framework(self, query: ProposalQuery) -> ProposalAgentResponse:
        if AzureAIAgentClient is None or MCPStreamableHTTPTool is None:
            raise RuntimeError("agent-framework not available; install dependency or unset AGENT_FRAMEWORK_MODE")
        if self.framework_client is None:
            raise RuntimeError("framework_client not provided for framework mode")

        # Instructions (concise) – detailed schema enforcement is handled by parsing & retry.
        instructions = _build_instructions(query.priority)
        agent_kwargs = dict(name="ProposalAgent", instructions=instructions)
        try:
            agent = self.framework_client.create_agent(response_format=ProposalAgentResponse, **agent_kwargs)  # type: ignore[arg-type]
        except TypeError:
            agent = self.framework_client.create_agent(**agent_kwargs)

        thread = agent.get_new_thread()
        user_prompt = (
            f"ユーザー要求: {query.user_query}\n"
            f"優先度: {query.priority}\n"
            f"制約: 予算={query.budget_max} 乗車人数={query.passenger_count} fuel_pref={query.fuel_pref}"
        )
        async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
            result = await agent.run(user_prompt, thread=thread, store=True, tools=mcp_server)

        # First parse attempt
        try:
            result.try_parse_value(output_format_type=ProposalAgentResponse)  # type: ignore[attr-defined]
        except Exception:
            pass

        # Retry if missing or empty recommendations
        if not getattr(result, "value", None) or not getattr(result.value, "recommendations", []):  # type: ignore[attr-defined]
            repair_prompt = (
                "前回出力はスキーマ不一致または recommendations が空です。必ず 1 件以上の候補を含む有効 JSON を出力してください。"
            )
            async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
                result2 = await agent.run(repair_prompt, thread=thread, store=True, tools=mcp_server)
            try:
                result2.try_parse_value(output_format_type=ProposalAgentResponse)  # type: ignore[attr-defined]
            except Exception:
                pass
            if getattr(result2, "value", None):
                result = result2

        if getattr(result, "value", None):
            return result.value  # type: ignore[return-value]

        # Fallback extraction from raw text
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
            # Post-process: if recommendations lack vehicle_price, fetch from VehicleModels
            if "recommendations" in extracted and isinstance(extracted["recommendations"], list):
                # Get vehicle models data to enrich recommendations with prices
                try:
                    vm = await self.mcp.call_tool("VehicleModels", {})  # type: ignore
                    models = vm.get("vehicle_models", [])
                    price_map = {}  # engine_id -> price mapping
                    for v in models:
                        for grade in v.get("grades", []):
                            for engine in grade.get("engine_options", []):
                                engine_id = engine.get("engine_id")
                                price = engine.get("price")
                                if engine_id and price:
                                    price_map[engine_id] = price
                    
                    # Enrich recommendations with vehicle_price
                    for rec in extracted["recommendations"]:
                        if "vehicle_price" not in rec or rec.get("vehicle_price") is None:
                            engine_id = rec.get("engine_id")
                            if engine_id and engine_id in price_map:
                                rec["vehicle_price"] = price_map[engine_id]
                            else:
                                # Fallback to budget_max if price not found
                                rec["vehicle_price"] = query.budget_max
                except Exception:
                    # If VehicleModels call fails, use budget_max as fallback
                    for rec in extracted["recommendations"]:
                        if "vehicle_price" not in rec:
                            rec["vehicle_price"] = query.budget_max
            
            try:
                return ProposalAgentResponse(**extracted)
            except Exception:
                pass

        # Final minimal fallback
        return ProposalAgentResponse(
            recommendations=[],
            normalized_requirements=NormalizedRequirements(
                budget_max=query.budget_max,
                passenger_count=query.passenger_count,
                priority=query.priority,
                fuel_pref=query.fuel_pref,
            ),
            next_action_hint="構造化失敗",
            metadata={"version": "1.0.0", "raw_output": txt},
        )

    async def run(self, query: ProposalQuery) -> ProposalAgentResponse:
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode == "framework":
            return await self._run_framework(query)
        # default procedural path
        if not self.mcp:
            raise RuntimeError("Procedural mode requires MCPToolClient instance")
        return await self._run_procedural(query)

