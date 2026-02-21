from pydantic import BaseModel, model_validator
from typing import Dict
from .base import SideModel


class BalerRequestModel(BaseModel):
    id: str
    images: Dict[str, SideModel]

    model_config = {
        "extra": "forbid"
    }

    @model_validator(mode="after")
    def validate_baler(self):

        if set(self.images.keys()) != {"side1"}:
            raise ValueError("baler 분류는 side1만 허용됩니다.")

        side1 = self.images["side1"]

        if side1.part1 is None or side1.part2 is None:
            raise ValueError("side1.part1, part2 모두 필요합니다.")

        return self