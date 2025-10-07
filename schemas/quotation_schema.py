from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SubscriptionBreakdown(BaseModel):
    base_fee: float = Field(..., description="ベース料金（車両分割相当）")
    maintenance_fee: Optional[float] = Field(0.0, description="月次メンテナンス料金")
    taxes_and_fees: Optional[float] = Field(0.0, description="月次税・手数料")
    discount_amount: Optional[float] = Field(0.0, description="適用された月次割引額")


class QuotationAgentResponse(BaseModel):
    engine_id: Optional[str] = Field(None, description="対象エンジンID")
    vehicle_price: Optional[float] = Field(None, description="車両価格（指定があれば）")
    subscription_term_months: int = Field(36, description="サブスク契約期間（月数])")
    monthly_fee: float = Field(..., description="計算された月額料金")
    breakdown: SubscriptionBreakdown = Field(..., description="月額内訳")
    total_cost: float = Field(..., description="契約期間中の総支払額")
    rationale: List[str] = Field(default_factory=list, description="計算根拠や注意事項")
    metadata: Dict[str, Any] = Field(default_factory=dict)
