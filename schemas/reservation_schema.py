from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ReservationQuery(BaseModel):
    """
    ReservationAgent への入力クエリ
        Fields:
            - customer_id: 顧客ID（デフォルト値 "GUEST_USER" を使用、ユーザへの質問は不要）
            - engine_id: 予約対象エンジンID（必須）
            - vehicle_id: 車両ID（任意）
            - grade_id: グレードID（任意）
            - preferred_times: ISO8601形式の希望時刻リスト（1-3候補）
            - reservation_type: 予約タイプ（例: "test_drive", "consultation"）
    """
    customer_id: str = Field(default="GUEST_USER", description="顧客ID（デフォルト: GUEST_USER）")
    engine_id: str = Field(..., description="予約対象エンジンID")
    vehicle_id: Optional[str] = Field(None, description="車両ID（任意）")
    grade_id: Optional[str] = Field(None, description="グレードID（任意）")
    preferred_times: List[str] = Field(..., description="ISO8601形式の希望時刻リスト（1-3候補）")
    reservation_type: Optional[str] = Field("test_drive", description="予約タイプ（例: test_drive, consultation）")


class ConflictInfo(BaseModel):
    time: str = Field(..., description="競合している時刻")
    reason: str = Field(..., description="競合理由")


class AlternativeTime(BaseModel):
    time: str = Field(..., description="代替可能な時刻")
    availability: str = Field(..., description="利用可能状況（例: available, limited）")


class ReservationAgentResponse(BaseModel):
    """
    ReservationAgent からの出力
        Fields:
            - reservation_id: 予約ID（予約確定時のみ）
            - confirmed: 予約が確定したか（bool）
            - chosen_time: 選択された時刻（確定時のみ）
            - alternatives: 代替候補時刻のリスト（競合時）
            - conflicts: 競合情報のリスト
            - next_action: 次のアクション提案（自然文）
            - metadata: メタ情報（version, generated_at 等）
    """
    reservation_id: Optional[str] = Field(None, description="予約ID（予約確定時のみ）")
    confirmed: bool = Field(..., description="予約が確定したか")
    chosen_time: Optional[str] = Field(None, description="選択された時刻（確定時のみ）")
    alternatives: Optional[List[AlternativeTime]] = Field(None, description="代替候補時刻のリスト")
    conflicts: Optional[List[ConflictInfo]] = Field(None, description="競合情報のリスト")
    next_action: str = Field(..., description="次のアクション提案")
    metadata: Dict[str, Any] = Field(..., description="メタ情報")
