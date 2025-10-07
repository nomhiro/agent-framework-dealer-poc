import asyncio
from typing import Any, Dict
from config import settings


_httpx = None

def _ensure_httpx():
    global _httpx
    if _httpx is None:
        import httpx as _h
        _httpx = _h
    return _httpx


class MCPToolClient:
    def __init__(self, endpoint: str = None, mock: bool = True):
        self.endpoint = endpoint or settings.MCP_ENDPOINT
        self.mock = mock or settings.MOCK_MCP

    async def call_tool(self, tool: str, input: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock:
            return await self._mock_call(tool, input)
        httpx = _ensure_httpx()
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.endpoint, json={"tool": tool, "input": input}, timeout=10.0)
            resp.raise_for_status()
            return resp.json()

    async def _mock_call(self, tool: str, input: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal deterministic mocked outputs for smoke tests
        await asyncio.sleep(0.05)
        if tool == "VehicleModels":
            return {
                "vehicle_models": [
                    {"model_id": "PRIUS", "grades": [{"grade_id": "U", "engine_options": [{"engine_id": "2.0HV-A", "price": 3500000}]}], "seats": 5, "fuel": "hybrid"},
                    {"model_id": "CROWN", "grades": [{"grade_id": "Sport", "engine_options": [{"engine_id": "2.4Turbo-HV", "price": 4800000}]}], "seats": 5, "fuel": "hybrid"},
                ]
            }
        if tool == "LeadTimeAPI":
            return {"items": [{"model_id": m, "est_lead_weeks": 6 if m == "PRIUS" else 8} for m in input.get("model_ids", [])]}
        if tool == "QuotationCalculator":
            # subscription monthly fee mock
            price = input.get("vehicle_price") or 4000000
            term = input.get("subscription_term_months", 36)
            maintenance = 5000 if input.get("maintenance_included") else 0
            discount_pct = float(input.get("discount_percent")) if input.get("discount_percent") else 0.0
            # base monthly = price / term * 0.01 (poC scaler) + maintenance
            base_fee = round((price / term) * 0.01, 2)
            monthly = base_fee + maintenance
            discount_amount = round(monthly * (discount_pct / 100.0), 2)
            monthly_after_discount = round(monthly - discount_amount, 2)
            taxes = round(monthly_after_discount * 0.1, 2)
            monthly_fee = round(monthly_after_discount + taxes, 2)
            breakdown = {
                "base_fee": base_fee,
                "maintenance_fee": maintenance,
                "discount_amount": discount_amount,
                "taxes_and_fees": taxes,
            }
            total_cost = round(monthly_fee * term, 2)
            return {
                "engine_id": input.get("engine_id"),
                "vehicle_price": price,
                "subscription_term_months": term,
                "monthly_fee": monthly_fee,
                "breakdown": breakdown,
                "total_cost": total_cost,
                "rationale": ["PoC subscription mock calculation"],
            }
        if tool == "FinancePrecheck":
            # Require top-level income and requested_amount
            if input.get("income") is None or input.get("requested_amount") is None:
                return {"error": True, "message": "必須パラメータが不足しています: income と requested_amount を指定してください。"}
            try:
                income = int(input.get("income"))
                requested = int(input.get("requested_amount"))
            except Exception:
                return {"error": True, "message": "income と requested_amount は数値で指定してください。"}
            # Simple PoC scoring (0-100)
            base = min(100, max(0, int((income / 10000) - (requested / 100000))))
            score = base
            rating = "AAA" if score > 90 else ("AA" if score > 80 else ("A" if score > 65 else "B"))
            approved = score >= 66
            return {
                "score": score,
                "rating": rating,
                "approved": approved,
                "annual_income": income,
                "requested_amount": requested,
            }
        if tool == "ReservationManager":
            return {"reservation_id": "r_123", "confirmed": True, "chosen_time": input.get("preferred_times", [])[0] if input.get("preferred_times") else None}
        return {"ok": True, "tool": tool, "input": input}
