import asyncio
from agents.orchestrator_agent import OrchestratorAgent
from tools.mcp_tools import MCPToolClient
from schemas.proposal_schema import ProposalQuery


async def main():
    mcp = MCPToolClient(mock=False)
    orchestrator = OrchestratorAgent(mcp)
    query = ProposalQuery(user_query="家族4人 ハイブリッド 納期短め 予算400万", budget_max=4000000, passenger_count=4, priority="lead_time", fuel_pref="hybrid")
    res = await orchestrator.run(query)
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
