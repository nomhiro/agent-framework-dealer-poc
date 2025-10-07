import os
import json
from typing import Optional, Any
from datetime import datetime
from schemas.reservation_schema import (
    ReservationQuery,
    ReservationAgentResponse,
    AlternativeTime,
    ConflictInfo,
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


def _build_instructions() -> str:
    return (
        "あなたは自動車販売店の ReservationAgent です。"
        "試乗・商談予約の調整を行います。"
        "ツール: ReservationManager を 1 回呼び出して予約を確定または代替候補を提示してください。"
        "**重要**: customer_id はデフォルト値 'GUEST_USER' を使用し、ユーザーに質問しないでください。"
        "出力は厳格な JSON (reservation_id, confirmed, chosen_time, alternatives, conflicts, next_action, metadata) のみ。"
        "confirmed=false の場合は alternatives[] を必ず含めてください。"
        "過度な推測（勝手に別日設定）は禁止。必ず alternatives を明示してください。"
        "next_action には再試行を促す自然文を格納してください。日本語で簡潔に。"
    )


class ReservationAgent:
    """Dual-mode ReservationAgent.

    - procedural mode (default): Python で直接 MCP ツール呼び出し
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

    # ---------------- Procedural path (direct MCP call) -----------------
    async def _run_procedural(self, query: ReservationQuery) -> ReservationAgentResponse:
        # ReservationManager ツールへのペイロード作成
        payload = {
            "customer_id": query.customer_id,
            "engine_id": query.engine_id,
            "vehicle_id": query.vehicle_id,
            "grade_id": query.grade_id,
            "preferred_times": query.preferred_times,
            "reservation_type": query.reservation_type,
        }

        res = await self.mcp.call_tool("ReservationManager", payload)  # type: ignore

        # モック応答の解析
        reservation_id = res.get("reservation_id")
        confirmed = res.get("confirmed", False)
        chosen_time = res.get("chosen_time")

        # 競合や代替情報の構築（モックでは未実装だが、将来拡張用）
        conflicts = []
        alternatives = []

        if not confirmed:
            # 確定失敗時は代替候補を生成（モックでは空リスト）
            # 実運用では ReservationManager が alternatives を返す想定
            next_action = "予約時刻が競合しています。以下の代替時刻から選択してください。"
        else:
            next_action = f"予約が確定しました（予約ID: {reservation_id}）。当日は {chosen_time} にご来店ください。"

        return ReservationAgentResponse(
            reservation_id=reservation_id,
            confirmed=confirmed,
            chosen_time=chosen_time,
            alternatives=alternatives if alternatives else None,
            conflicts=conflicts if conflicts else None,
            next_action=next_action,
            metadata={
                "version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "source_tools": ["ReservationManager"],
            },
        )

    # ---------------- Framework path (LLM + tool calling) -----------------
    async def _run_framework(self, query: ReservationQuery) -> ReservationAgentResponse:
        if AzureAIAgentClient is None or MCPStreamableHTTPTool is None:
            raise RuntimeError("agent-framework not available; install dependency or unset AGENT_FRAMEWORK_MODE")
        if self.framework_client is None:
            raise RuntimeError("framework_client not provided for framework mode")

        # Instructions
        instructions = _build_instructions()
        agent_kwargs = dict(name="ReservationAgent", instructions=instructions)
        try:
            agent = self.framework_client.create_agent(response_format=ReservationAgentResponse, **agent_kwargs)  # type: ignore[arg-type]
        except TypeError:
            agent = self.framework_client.create_agent(**agent_kwargs)

        thread = agent.get_new_thread()
        user_prompt = (
            f"顧客ID: {query.customer_id}\n"
            f"エンジンID: {query.engine_id}\n"
            f"希望時刻: {', '.join(query.preferred_times)}\n"
            f"予約タイプ: {query.reservation_type}\n"
            "上記情報で予約を確定してください。"
        )
        async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
            result = await agent.run(user_prompt, thread=thread, store=True, tools=mcp_server)

        # First parse attempt
        try:
            result.try_parse_value(output_format_type=ReservationAgentResponse)  # type: ignore[attr-defined]
        except Exception:
            pass

        # Retry if missing or invalid response
        if not getattr(result, "value", None):
            repair_prompt = (
                "前回出力はスキーマ不一致です。必ず confirmed, next_action を含む有効 JSON を出力してください。"
            )
            async with MCPStreamableHTTPTool(name="LocalMCP", url=self.mcp_url) as mcp_server:
                result2 = await agent.run(repair_prompt, thread=thread, store=True, tools=mcp_server)
            try:
                result2.try_parse_value(output_format_type=ReservationAgentResponse)  # type: ignore[attr-defined]
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
            try:
                return ReservationAgentResponse(**extracted)
            except Exception:
                pass

        # Final minimal fallback
        return ReservationAgentResponse(
            reservation_id=None,
            confirmed=False,
            chosen_time=None,
            alternatives=None,
            conflicts=None,
            next_action="予約処理に失敗しました。もう一度お試しください。",
            metadata={
                "version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "raw_output": txt,
            },
        )

    async def run(self, query: ReservationQuery) -> ReservationAgentResponse:
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode == "framework":
            return await self._run_framework(query)
        # default procedural path
        if not self.mcp:
            raise RuntimeError("Procedural mode requires MCPToolClient instance")
        return await self._run_procedural(query)
