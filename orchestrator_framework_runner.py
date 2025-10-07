"""Framework-based Orchestrator runner

Uses AzureAIAgentClient + MCPStreamableHTTPTool via child agents (framework mode).

Prerequisites:
  - az login
  - Environment variables for Azure AI Project (e.g. azure_ai_project_endpoint, azure_ai_model_deployment_name, etc.)
  - Local MCP Azure Functions running (default: http://localhost:7071/runtime/webhooks/mcp)

Example:
  powershell>
    $env:AGENT_FRAMEWORK_MODE="framework"; \
    $env:MCP_SERVER_URL="http://localhost:7071/runtime/webhooks/mcp"; \
    python orchestrator_framework_runner.py --query "家族4人 ハイブリッド 納期短め 予算400万" --priority lead_time
"""
from __future__ import annotations

import os
import argparse
import asyncio
import json
import logging
from typing import Optional

from azure.identity.aio import AzureCliCredential

try:
    from agent_framework.azure import AzureAIAgentClient
except ImportError:  # pragma: no cover
    raise SystemExit("agent-framework が未インストールです。pyproject.toml を確認してください。")

from agents.orchestrator_agent import OrchestratorAgent
from schemas.proposal_schema import ProposalQuery


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Framework Orchestrator Runner")
    p.add_argument("--query", required=True, help="ユーザー要求")
    p.add_argument("--priority", default="balance", choices=["lead_time", "price", "balance"], help="優先度")
    p.add_argument("--fuel-pref", default="hybrid", choices=["hybrid", "gasoline", "ev", "any"], help="燃料優先")
    p.add_argument("--budget-max", type=int, default=4000000)
    p.add_argument("--passenger-count", type=int, default=4)
    p.add_argument("--debug", action="store_true")
    return p.parse_args()


REQUIRED_ENV_HINT = [
    "AZURE_AI_PROJECT_ENDPOINT",
    "AZURE_AI_PROJECT_DEPLOYMENT",
    "AZURE_AI_MODEL_DEPLOYMENT_NAME",  # depending on agent-framework version naming may differ
]


def validate_env() -> list[str]:
    missing = []
    for k in REQUIRED_ENV_HINT:
        if not os.getenv(k):
            missing.append(k)
    return missing


async def run_once(args: argparse.Namespace) -> None:
    # Force framework mode for child agents
    os.environ.setdefault("AGENT_FRAMEWORK_MODE", "framework")
    os.environ.setdefault("MCP_SERVER_URL", os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp"))

    missing = validate_env()
    if missing:
        print("[WARN] Azure AI Project 関連の環境変数が不足しています: " + ", ".join(missing))
        print("       プロジェクト設定が agent-framework 側で自動解決できない場合は失敗する可能性があります。")

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    async with AzureCliCredential() as cred, AzureAIAgentClient(async_credential=cred) as client:
        orchestrator = OrchestratorAgent(mcp=None, framework_client=client)
        query = ProposalQuery(
            user_query=args.query,
            budget_max=args.budget_max,
            passenger_count=args.passenger_count,
            priority=args.priority,
            fuel_pref=args.fuel_pref if args.fuel_pref != "any" else None,
        )
        result = await orchestrator.run(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    asyncio.run(run_once(args))


if __name__ == "__main__":
    main()
