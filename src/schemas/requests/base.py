from pydantic import BaseModel, Field
from typing import Optional


class SideModel(BaseModel):
    part1: str = Field(..., description="이미지 경로 (필수)")
    part2: Optional[str] = Field(None, description="이미지 경로 (선택)")

    model_config = {
        "extra": "forbid"
    }