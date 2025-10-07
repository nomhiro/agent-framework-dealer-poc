"""
Simple test script for ReservationAgent (procedural mode)
"""
import asyncio
from agents.reservation_agent import ReservationAgent
from schemas.reservation_schema import ReservationQuery
from tools.mcp_tools import MCPToolClient


async def main():
    print("=== ReservationAgent Test (Procedural Mode) ===\n")

    # Initialize MCP client with mock mode
    mcp = MCPToolClient(mock=True)

    # Create ReservationAgent
    agent = ReservationAgent(mcp=mcp)

    # Test 1: Successful reservation
    print("Test 1: Successful reservation with default customer_id")
    query1 = ReservationQuery(
        engine_id="2.0HV-A",
        vehicle_id="PRIUS",
        grade_id="U",
        preferred_times=["2025-10-10T10:00:00Z", "2025-10-10T14:00:00Z"],
        reservation_type="test_drive",
    )

    result1 = await agent.run(query1)
    print(f"  Customer ID: {query1.customer_id}")
    print(f"  Reservation ID: {result1.reservation_id}")
    print(f"  Confirmed: {result1.confirmed}")
    print(f"  Chosen Time: {result1.chosen_time}")
    print(f"  Next Action: {result1.next_action}")
    print(f"  Metadata: {result1.metadata}")
    print()

    # Test 2: Reservation with explicit customer_id
    print("Test 2: Reservation with explicit customer_id")
    query2 = ReservationQuery(
        customer_id="CUSTOMER_12345",
        engine_id="2.4Turbo-HV",
        vehicle_id="CROWN",
        grade_id="Sport",
        preferred_times=["2025-10-11T15:00:00Z"],
        reservation_type="consultation",
    )

    result2 = await agent.run(query2)
    print(f"  Customer ID: {query2.customer_id}")
    print(f"  Reservation ID: {result2.reservation_id}")
    print(f"  Confirmed: {result2.confirmed}")
    print(f"  Chosen Time: {result2.chosen_time}")
    print(f"  Next Action: {result2.next_action}")
    print()

    print("=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(main())
