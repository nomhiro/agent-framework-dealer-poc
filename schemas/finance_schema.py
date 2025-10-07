from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FinanceAdvisorQuery(BaseModel):
    """
    FinanceAdvisorAgent への入力クエリ
        Fields (トップレベル):
            - selected_plan: QuotationAgent の推奨プラン dict
            - income: 顧客の年収（円） — 必須
            - requested_amount: 希望借入額（円） — 必須
            - age, employment_status, existing_debt, dependents は任意
    """
    selected_plan: Dict[str, Any] = Field(..., description="QuotationAgent 推奨プラン")
    income: int = Field(..., description="顧客の年収（円）")
    requested_amount: int = Field(..., description="希望借入額（円）")
    age: Optional[int] = Field(None, description="顧客の年齢（任意）")
    employment_status: Optional[str] = Field(None, description="雇用形態（任意、例: 正社員/派遣/自営業）")
    existing_debt: Optional[int] = Field(None, description="既存の借入残高（任意、円）")
    dependents: Optional[int] = Field(None, description="扶養人数（任意）")

class Factor(BaseModel):
    name: str = Field(..., description="要因名")
    impact: int = Field(..., description="要因がスコアへ及ぼす影響")

class FinanceAdvisorResponse(BaseModel):
    # PoC 出力: MCP の FinancePrecheck と整合するフィールドをトップレベルで持ちます
    score: int = Field(..., description="与信スコア (0-100)")
    rating: str = Field(..., description="評価ランク (AAA/AA/A/B)")
    approved: bool = Field(..., description="与信判定: 承認なら True")
    annual_income: int = Field(..., description="与信で使用した年収 (円)")
    requested_amount: int = Field(..., description="与信で使用した希望借入額 (円)")
    # 既存の内部向けフィールド
    decision: Optional[str] = Field(None, description="高レベル判定 (approved/manual_review/reject)")
    factors: Optional[List[Factor]] = Field(None, description="要因内訳 (A: explainability)")
    manual_review_reason: Optional[str] = Field(None, description="人手レビュー理由 (manual_review 時)")
    metadata: Dict[str, Any] = Field(..., description="メタ情報 (version, source_tools, generated_at)")
