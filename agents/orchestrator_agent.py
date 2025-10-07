from tools.mcp_tools import MCPToolClient
from agents.proposal_agent import ProposalAgent
from agents.quotation_agent import QuotationAgent
from agents.finance_agent import FinanceAdvisorAgent
from schemas.finance_schema import FinanceAdvisorQuery
from schemas.proposal_schema import ProposalQuery
from datetime import datetime
from typing import Dict, Any, Optional
import os
import json

try:  # Azure client (framework mode)
    from agent_framework.azure import AzureAIAgentClient
    from agent_framework import ChatAgent  # for type hints / future direct usage
except ImportError:  # pragma: no cover
    AzureAIAgentClient = None  # type: ignore
    ChatAgent = None  # type: ignore


FRAMEWORK_MODE_ENV = "AGENT_FRAMEWORK_MODE"


class OrchestratorAgent:
    """Orchestrator that can operate in two modes:

    1. Procedural (default): Python decides call order Proposal -> Quotation.
    2. LLM orchestration (AGENT_FRAMEWORK_MODE=framework): LLM receives tools that invoke child agents and decides when/how to call them.

    LLMモードでは multi-turn 会話に対応するため内部で framework ChatAgent と Thread を保持し、
    ユーザー入力毎に同一 thread を用いて context を維持する。ユーザーは最初の要求で提案と見積り、
    追加の質問で再計算や別エンジン比較などを継続的に依頼できる。

        提供ツール:
            - call_proposal(user_query, budget_max, passenger_count, priority, fuel_pref)
            - call_quotation(engine_id, vehicle_price, down_payment)
            - call_finance(income, requested_amount, age, employment_status, existing_debt, dependents)
              ※ selected_plan は内部で自動設定されるため LLM からの指定は不要

    各 turn の最終出力は "machine_output" (JSON) と "assistant_output" (LLM自然文) を含む辞書形式で返す。
    machine_output は {workflow_state, agents:{proposal, quotation}, metadata} を可能な限り保持する。
    """

    def __init__(self, mcp: Optional[MCPToolClient] = None, framework_client: Optional[Any] = None):
        self.mcp = mcp
        self.framework_client = framework_client
        self.proposal = ProposalAgent(mcp=mcp, framework_client=framework_client)
        self.quotation = QuotationAgent(mcp=mcp, framework_client=framework_client)
        self.finance = FinanceAdvisorAgent(mcp=mcp, framework_client=framework_client)
        # --- framework multi-turn state ---
        self._framework_agent = None  # type: ignore
        self._framework_thread = None  # type: ignore
        self._framework_instructions = None
        # --- state preservation for tool calls ---
        self._last_quotation: Optional[Dict[str, Any]] = None  # Store latest quotation for finance calls
        self._last_proposal: Optional[Dict[str, Any]] = None   # Store latest proposal
        self._last_finance: Optional[Dict[str, Any]] = None    # Store latest finance result

    # ---------------- Procedural path ----------------
    async def _run_procedural(self, query: ProposalQuery) -> Dict[str, Any]:
        prop = await self.proposal.run(query)
        if not prop.recommendations:
            return {"workflow_state": "failed", "reason": "no_recommendations"}
        first = prop.recommendations[0]
        vehicle_price = first.vehicle_price
        quote = await self.quotation.run(first.engine_id or "", vehicle_price)
        # FinanceAdvisorAgent 呼び出し
        from schemas.finance_schema import FinanceAdvisorQuery  # avoid circular import
        # Procedural モードではダミーの与信入力（例）を使用。実運用ではユーザー入力か CRM 連携で取得。
        fin_query = FinanceAdvisorQuery(
            selected_plan=quote.dict(),
            income=6_000_000,
            requested_amount=vehicle_price // 2,
            age=35,
            employment_status="正社員",
            existing_debt=0,
            dependents=0,
        )
        fin = await self.finance.run(fin_query)
        return {
            "workflow_state": "completed",
            "agents": {"proposal": prop.dict(), "quotation": quote.dict(), "finance": fin.dict()},
            "metadata": {"version": "1.0.0", "generated_at": datetime.utcnow().isoformat()},
        }

    # ---------------- LLM Orchestration path ----------------
    def _framework_instructions_text(self) -> str:
        return (
            "あなたは自動車販売オーケストレーターです。ユーザーとの複数ターン会話で要求を整理し、"
            "必要に応じて call_proposal で候補生成、"
            "call_quotation でサブスクリプション月額（monthly_fee）を算出、"
            "call_finance で与信審査可能です。"
            "ユーザーからの要求を満たすために必要な手順を自律的に判断し、適切なツールを呼び出してください。\n\n"
            "ツール呼び出しガイド:\n"
            "- call_quotation には engine_id のみを渡してください。vehicle_price は proposal 結果から自動取得されます。"
            "- call_finance を呼ぶ際: selected_plan は自動設定されるため指定不要。income, requested_amount は必須。ユーザーから得られていない場合は一度に質問してから実行。\n"
            "- age, employment_status, existing_debt, dependents はオプションですが、取得可能であれば渡してください。\n\n"
            "応答形式:\n"
            "ユーザーへの応答は自然な日本語で簡潔に返してください。内部の JSON 構造や技術的な詳細は表示しないでください。\n"
            "例: 「トヨタのHARRIERをおすすめします。月額料金は69,020円、契約期間は36ヶ月です。さらにご検討が必要であればお知らせください。」\n\n"
            "不足情報がある場合は、どの項目が不足しているかを明示して質問してください。\n"
            "ツール呼び出し前に必要な情報が揃っているか確認し、不足している場合はユーザーに質問してから再試行してください。"
        )

    async def _ensure_framework_agent(self) -> None:
        if self._framework_agent is not None:
            return
        if AzureAIAgentClient is None or self.framework_client is None:
            raise RuntimeError("Framework client not available for LLM orchestration mode")

        # --- tool wrappers (defined once so docstrings become tool descriptions) ---
        async def call_proposal(
            user_query: str,
            budget_max: Optional[int] = None,
            passenger_count: Optional[int] = None,
            priority: Optional[str] = None,
            fuel_pref: Optional[str] = None,
        ) -> dict:
            """顧客要求を基に候補車種リスト(recommendations)と要約(normalized_requirements)を返す。納期短縮重視は priority='lead_time'。"""
            pq = ProposalQuery(
                user_query=user_query,
                budget_max=budget_max,
                passenger_count=passenger_count,
                priority=priority,
                fuel_pref=fuel_pref,
            )
            resp = await self.proposal.run(pq)
            result = resp.dict()
            self._last_proposal = result
            return result

        async def call_quotation(
            engine_id: str,
            down_payment: Optional[int] = 0,
        ) -> dict:
            """proposalで選択した engine_id に対しローン/支払プラン計算結果を返す。
            vehicle_price は proposal 結果から自動取得されます。"""
            # Find vehicle_price from last_proposal recommendations
            vehicle_price = None
            if self._last_proposal:
                for rec in self._last_proposal.get("recommendations", []):
                    if rec.get("engine_id") == engine_id:
                        vehicle_price = rec.get("vehicle_price")
                        break
            if vehicle_price is None:
                raise ValueError(f"engine_id {engine_id} not found in proposal results or price missing")
            resp = await self.quotation.run(engine_id, vehicle_price, down_payment or 0)
            result = resp.dict()
            # Store for later finance call
            self._last_quotation = result
            return result

        async def call_finance(
            income: int,
            requested_amount: int,
            age: Optional[int] = None,
            employment_status: Optional[str] = None,
            existing_debt: Optional[int] = None,
            dependents: Optional[int] = None,
        ) -> dict:
            """与信スコアリング実行。
            
            必須パラメータ:
              - income (int): 顧客年収（円）
              - requested_amount (int): 希望借入額（円）
            
            オプション: age, employment_status, existing_debt, dependents
            
            注: selected_plan は直前の call_quotation 結果を自動的に使用します（LLM は指定不要）。
            """
            from schemas.finance_schema import FinanceAdvisorQuery
            
            if self._last_quotation is None:
                return {
                    "error": True,
                    "message": "call_finance を呼ぶ前に call_quotation を実行してください。"
                }
            
            faq = FinanceAdvisorQuery(
                selected_plan=self._last_quotation,
                income=income,
                requested_amount=requested_amount,
                age=age,
                employment_status=employment_status,
                existing_debt=existing_debt,
                dependents=dependents,
            )
            fresp = await self.finance.run(faq)
            result = fresp.dict()
            self._last_finance = result
            return result

        self._framework_instructions = self._framework_instructions_text()
        self._framework_agent = self.framework_client.create_agent(
            name="OrchestratorAgent",
            instructions=self._framework_instructions,
            tools=[call_proposal, call_quotation, call_finance],
        )
        self._framework_thread = self._framework_agent.get_new_thread()

    @staticmethod
    def _extract_machine_output(text: str) -> Dict[str, Any]:
        """Best-effort JSON extraction. Accepts either full wrapper {assistant_output, machine_output} or legacy {workflow_state,...}."""
        candidate: Dict[str, Any] | None = None
        if "{" not in text:
            return {"workflow_state": "failed", "reason": "no_json", "raw": text[:2000]}
        start = text.find("{")
        end = text.rfind("}") + 1
        try:
            parsed = json.loads(text[start:end])
            if isinstance(parsed, dict):
                if "machine_output" in parsed:
                    # already wrapper form
                    return parsed  # type: ignore[return-value]
                else:
                    candidate = parsed
        except Exception:
            return {"workflow_state": "failed", "reason": "parse_error", "raw": text[:2000]}
        # wrap legacy
        if candidate and "workflow_state" in candidate:
            return {"assistant_output": "", "machine_output": candidate}
        return {"assistant_output": "", "machine_output": {"workflow_state": "failed", "reason": "unexpected_format", "raw": text[:2000]}}

    async def _framework_turn(self, user_message: str) -> Dict[str, Any]:
        await self._ensure_framework_agent()
        result = await self._framework_agent.run(user_message, thread=self._framework_thread, store=True)
        text = getattr(result, "text", str(result))
        
        # Use LLM output directly as assistant_output (natural language)
        assistant_output = text.strip()
        
        # Build machine_output from internal state (tool call results)
        machine_output: Dict[str, Any] = {
            "workflow_state": "in_progress",
            "agents": {},
            "metadata": {
                "version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
            }
        }
        
        # Include all available agent results
        if self._last_proposal:
            machine_output["agents"]["proposal"] = self._last_proposal
        if self._last_quotation:
            machine_output["agents"]["quotation"] = self._last_quotation
            machine_output["workflow_state"] = "quotation_obtained"
        if self._last_finance:
            machine_output["agents"]["finance"] = self._last_finance
            machine_output["workflow_state"] = "completed"
        
        return {
            "assistant_output": assistant_output,
            "machine_output": machine_output
        }

    async def start_chat(self, initial_query: ProposalQuery) -> Dict[str, Any]:
        """Start a multi-turn chat session (framework mode). Returns first turn response.

        In procedural mode this simply runs once and returns procedural result wrapped.
        """
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode != "framework":
            proc = await self._run_procedural(initial_query)
            return {"assistant_output": "(procedural single turn)", "machine_output": proc}
        seed_msg = (
            f"初期ユーザー要求: {initial_query.user_query}\n"
            f"予算: {initial_query.budget_max} 乗車人数: {initial_query.passenger_count} 優先度: {initial_query.priority} fuel_pref: {initial_query.fuel_pref or 'unspecified'}\n"
            "必要なツールを利用して候補と見積を用意し、フォーマット指示に従って返してください。"
        )
        return await self._framework_turn(seed_msg)

    async def chat_turn(self, user_message: str) -> Dict[str, Any]:
        """Subsequent multi-turn user message (framework mode only)."""
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode != "framework":
            return {"assistant_output": "framework mode ではありません", "machine_output": {"workflow_state": "unsupported"}}
        return await self._framework_turn(user_message)

    async def _run_llm_orchestration(self, query: ProposalQuery) -> Dict[str, Any]:
        """Backward compatible single-shot orchestration (first turn of chat)."""
        response = await self.start_chat(query)
        return response.get("machine_output", response)  # keep legacy contract for run()

    async def run(self, query: ProposalQuery) -> Dict[str, Any]:
        mode = os.getenv(FRAMEWORK_MODE_ENV, "procedural").lower()
        if mode == "framework":
            return await self._run_llm_orchestration(query)
        return await self._run_procedural(query)

    def reset_thread(self) -> None:
        """Reset the internal framework thread.

        This allows the REPL (or other callers) to start a fresh conversation
        without restarting the whole process. If the framework agent exists,
        a new thread is created; otherwise the thread is cleared.
        """
        if getattr(self, "_framework_agent", None):
            try:
                self._framework_thread = self._framework_agent.get_new_thread()
            except Exception:
                self._framework_thread = None
        else:
            self._framework_thread = None
