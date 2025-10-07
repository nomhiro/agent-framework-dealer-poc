"""Interactive multi-turn chat REPL for OrchestratorAgent (framework mode).

Usage (PowerShell):
  $env:AGENT_FRAMEWORK_MODE="framework"
  python orchestrator_chat_repl.py --query "家族4人 ハイブリッド 納期短め 予算400万" --priority lead_time

Type: /exit で終了, /json で最新 machine_output を表示, /help でヘルプ。
Requires Azure AI project env + az login + running MCP endpoint if tools needed.

Logging:
  --verbose: 詳細ログを有効化（DEBUG レベル）
  --log-file: ログをファイルに出力
"""
from __future__ import annotations

import asyncio
import argparse
import json
import os
import logging
import sys
from typing import Optional

from azure.identity.aio import AzureCliCredential
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import setup_observability

from agents.orchestrator_agent import OrchestratorAgent
from schemas.proposal_schema import ProposalQuery


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Configure logging for the REPL."""
    level = logging.DEBUG if verbose else logging.INFO
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )
    
    # Set specific loggers
    logging.getLogger('orchestrator_chat_repl').setLevel(level)
    logging.getLogger('agents').setLevel(level)
    logging.getLogger('tools').setLevel(level)
    
    # Reduce noise from Azure SDK
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Orchestrator multi-turn chat REPL")
    p.add_argument("--query", required=True, help="初回ユーザー要求")
    p.add_argument("--priority", default="balance", choices=["lead_time", "price", "balance"], help="優先度")
    p.add_argument("--fuel-pref", default="hybrid", choices=["hybrid", "gasoline", "ev", "any"], help="燃料優先")
    p.add_argument("--budget-max", type=int, default=4000000)
    p.add_argument("--passenger-count", type=int, default=4)
    p.add_argument("--verbose", action="store_true", help="詳細ログを有効化（DEBUG レベル）")
    p.add_argument("--log-file", type=str, help="ログをファイルに出力")
    p.add_argument("--enable-otel", action="store_true", help="OpenTelemetry トレースを有効化")
    return p.parse_args()


async def run_chat(args: argparse.Namespace) -> None:
    logger = logging.getLogger('orchestrator_chat_repl')
    
    os.environ.setdefault("AGENT_FRAMEWORK_MODE", "framework")
    os.environ.setdefault("MCP_SERVER_URL", os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp"))

    # Enable observability if requested
    if args.enable_otel:
        logger.info("Enabling OpenTelemetry observability...")
        setup_observability(enable_sensitive_data=True)
    
    logger.info(f"Starting REPL with query: {args.query}")
    logger.debug(f"Config: priority={args.priority}, fuel={args.fuel_pref}, budget={args.budget_max}")

    async with AzureCliCredential() as cred, AzureAIAgentClient(async_credential=cred) as client:
        # Initialize orchestrator and start first chat
        logger.info("Creating OrchestratorAgent...")
        
        # Create MCP client for procedural fallback in framework mode
        from tools.mcp_tools import MCPToolClient
        mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")
        mcp_client = MCPToolClient(mcp_url)
        
        orch = OrchestratorAgent(mcp=mcp_client, framework_client=client)
        
        query = ProposalQuery(
            user_query=args.query,
            budget_max=args.budget_max,
            passenger_count=args.passenger_count,
            priority=args.priority,
            fuel_pref=args.fuel_pref if args.fuel_pref != "any" else None,
        )
        
        logger.info("Sending initial query to orchestrator...")
        first = await orch.start_chat(query)
        latest_machine = first.get("machine_output")
        
        logger.debug(f"Initial response machine_output: {json.dumps(latest_machine, ensure_ascii=False, indent=2)}")
        
        print("=== 初回応答 ===")
        print(first.get("assistant_output"))
        
        while True:
            user = input("あなた> ").strip()
            if not user:
                continue
            
            logger.debug(f"User input: {user}")
            
            if user.lower() in {"/exit", "exit", ":q", "quit"}:
                print("終了します。")
                logger.info("User requested exit")
                break
            if user.lower() in {"/help", "help"}:
                print("/json  現在保持している machine_output を表示\n/reset 会話を新規作成\n/exit 終了")
                continue
            if user.lower() in {"/reset", "reset"}:
                print("会話を新規作成します。新しいクエリを入力してください（形式: SUV 400万 4名 コスパ ハイブリッド）")
                user_new_query = input("新しいクエリ> ").strip()
                if not user_new_query:
                    print("クエリが空です。リセットをキャンセルしました。")
                    continue
                
                logger.info(f"Resetting conversation with new query: {user_new_query}")
                
                # Recreate orchestrator instance to avoid incomplete run state
                orch = OrchestratorAgent(mcp=mcp_client, framework_client=client)
                new_query = ProposalQuery(
                    user_query=user_new_query,
                    budget_max=args.budget_max,
                    passenger_count=args.passenger_count,
                    priority=args.priority,
                    fuel_pref=args.fuel_pref if args.fuel_pref != "any" else None,
                )
                first = await orch.start_chat(new_query)
                latest_machine = first.get("machine_output")
                
                logger.debug(f"Reset response machine_output: {json.dumps(latest_machine, ensure_ascii=False, indent=2)}")
                
                print("=== 初回応答 ===")
                print(first.get("assistant_output"))
                continue
            if user.lower() == "/json":
                print(json.dumps(latest_machine, ensure_ascii=False, indent=2))
                continue
            
            logger.info(f"Sending chat turn: {user}")
            try:
                resp = await orch.chat_turn(user)
                latest_machine = resp.get("machine_output", latest_machine)
                
                logger.debug(f"Response machine_output: {json.dumps(latest_machine, ensure_ascii=False, indent=2)}")
                
                print("--- 応答 ---")
                print(resp.get("assistant_output"))
            except Exception as e:
                logger.exception(f"Error during chat turn: {e}")
                print(f"エラーが発生しました: {e}")
                print("詳細はログファイルを確認してください。")


def main() -> None:
    args = parse_args()
    setup_logging(verbose=args.verbose, log_file=args.log_file)
    
    logger = logging.getLogger('orchestrator_chat_repl')
    logger.info("=== Orchestrator Chat REPL Starting ===")
    
    try:
        asyncio.run(run_chat(args))
    except KeyboardInterrupt:
        logger.info("User interrupted with Ctrl+C")
        print("\n中断されました。")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n予期しないエラーが発生しました: {e}")
        if args.log_file:
            print(f"詳細はログファイルを確認してください: {args.log_file}")
        raise


if __name__ == "__main__":
    main()
