from pydantic import BaseModel
from typing import List, Optional

class AdRemovalMarkerBase(BaseModel):
    marker_time_ms: int
    marker_order: int

class AdRemovalMarkerCreate(AdRemovalMarkerBase):
    pass

class AdRemovalMarker(AdRemovalMarkerBase):
    id: int
    rule_id: int

    class Config:
        orm_mode = True

class AdRemovalRuleBase(BaseModel):
    subscription_id: int
    strategy: str # ENUM('remove_before', 'remove_after', 'remove_between')

class AdRemovalRuleCreate(AdRemovalRuleBase):
    markers: List[AdRemovalMarkerCreate] = []

class AdRemovalRule(AdRemovalRuleBase):
    id: int
    markers: List[AdRemovalMarker] = []

    class Config:
        orm_mode = True
