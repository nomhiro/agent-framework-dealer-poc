import os
import json
from datetime import datetime
from typing import Optional, Any, Dict
from schemas.finance_schema import FinanceAdvisorQuery, FinanceAdvisorResponse
from tools.mcp_tools import MCPToolClient

# Optional framework imports
try:
    from agent_framework import MCPStreamableHTTPTool, AgentThread
    from agent_framework.azure import AzureAIAgentClient
except ImportError:
    MCPStreamableHTTPTool = None  # type: ignore
    AzureAIAgentClient = None  # type: ignore
    AgentThread = None  # type: ignore

FRAMEWORK_MODE_ENV = "AGENT_FRAMEWORK_MODE"


def _build_instructions() -> str:
    return (
        "あなたは融資アドバイザーエージェントです。ユーザーの顧客属性（income, requested_amount, age, employment_status, existing_debt, dependents）を基に、"
        "FinancePrecheck ツールを呼び出して信用プレチェックを行い、MCP の返却仕様に従ってトップレベルで score, rating, approved, annual_income, requested_amount を返してください。"
        "出力は厳格な JSON のみとし、もし必須情報（income または requested_amount）が不足している場合は、日本語のエラーメッセージを message フィールドで返すこと。"
    )


class FinanceAdvisorAgent:
    """Dual-mode FinanceAdvisorAgent: procedural (MCP) or framework (LLM+tool)."""

    def __init__(
        self,
        mcp: Optional[MCPToolClient] = None,
        framework_client: Optional[Any] = None,
        mcp_url: Optional[str] = None,
    ):
        self.mcp = mcp
        self.framework_client = framework_client
        self.mcp_url = mcp_url or os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")

    async def _run_procedural(self, query: FinanceAdvisorQuery) -> FinanceAdvisorResponse:
        payload = query.dict()
        res = await self.mcp.call_tool("FinancePrecheck", payload)  # type: ignore
        # Handle MCP error response
        if res.get("error"):
            metadata = {
                "version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "source_tools": ["FinancePrecheck"],
            }
            return FinanceAdvisorResponse(
                score=0,
                rating="",
                approved=False,
                annual_income=query.income or 0,
                requested_amount=query.requested_amount or 0,
                decision="manual_review",
                factors=None,
                manual_review_reason=res.get("message"),
                metadata=metadata,
            )
        # Map successful result to response schema
        metadata = {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "source_tools": ["FinancePrecheck"],
        }
        return FinanceAdvisorResponse(
            score=res.get("score", 0),
            rating=res.get("rating", ""),
            approved=bool(res.get("approved", False)),
            annual_income=res.get("annual_income", query.income),
            requested_amount=res.get("requested_amount", query.requested_amount),
            decision=("approved" if res.get("approved") else "manual_review"),
            factors=None,
            manual_review_reason=None,
            metadata=metadata,
        )

    async def _run_framework(self, query: FinanceAdvisorQuery) -> FinanceAdvisorResponse:
        if AzureAIAgentClient is None or MCPStreamableHTTPTool is None:
            raise RuntimeError("agent-framework not available; unset framework mode or install dependencies")
        if self.framework_client is None:
            raise RuntimeError("framework_client not provided")

        instructions = _build_instructions()
        agent_kwargs = dict(name="FinanceAdvisorAgent", instructions=instructions)
        try:
            agent = self.framework_client.create_agent(response_format=FinanceAdvisorResponse, **agent_kwargs)  # type: ignore[arg-type]
        except TypeError:
            agent = self.framework_client.create_agent(**agent_kwargs)

        thread = agent.get_new_thread()
        # Build prompt based on finance schema fields
        user_prompt = (
            f"income: {query.income}\n"
            f"requested_amount: {query.requested_amount}\n"
            f"age: {query.age or 'unspecified'}\n"
            f"employment_status: {query.employment_status or 'unspecified'}\n"
            f"existing_debt: {query.existing_debt or 0}\n"
            f"dependents: {query.dependents or 0}\n"
            "上記情報を基に FinancePrecheck と同等のトップレベル出力 (score, rating, approved, annual_income, requested_amount) を返してください。必須パラメータが欠ける場合は日本語のエラーメッセージを message に含めてください。"
        )
        async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
            result = await agent.run(user_prompt, thread=thread, store=True, tools=mcp_server)
        # Attempt structured parse
        try:
            result.try_parse_value(output_format_type=FinanceAdvisorResponse)  # type: ignore[attr-defined]
        except Exception:
            pass
        if getattr(result, "value", None):
            return result.value  # type: ignore[return-value]
        # Fallback: use procedural
        return await self._run_procedural(query)

    async def run(self, query: FinanceAdvisorQuery) -> FinanceAdvisorResponse:
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode == "framework":
            return await self._run_framework(query)
        if not self.mcp:
            raise RuntimeError("Procedural mode requires MCPToolClient instance")
        return await self._run_procedural(query)
