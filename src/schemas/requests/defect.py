from pydantic import BaseModel, model_validator
from typing import Dict, Optional
from .base import SideModel


class DefectRequestModel(BaseModel):
    id: str
    baler: Optional[int] = None
    images: Dict[str, SideModel]

    model_config = {
        "extra": "forbid"
    }

    @model_validator(mode="after")
    def validate_defect(self):

        if not self.images:
            raise ValueError("images가 필요합니다.")

        required_sides = {"side1", "side2", "side3"}

        if not required_sides.issubset(set(self.images.keys())):
            raise ValueError("side1, side2, side3은 필수입니다.")

        for key in self.images.keys():
            if not key.startswith("side"):
                raise ValueError(f"{key} 는 잘못된 key입니다.")

            num = int(key.replace("side", ""))
            if num < 1 or num > 6:
                raise ValueError("side는 1~6만 허용됩니다.")

        for s in ["side1", "side2", "side3"]:
            side = self.images[s]
            if side.part1 is None or side.part2 is None:
                raise ValueError(f"{s}.part1, part2 모두 필요합니다.")

        for s in ["side4", "side5", "side6"]:
            if s in self.images:
                if self.images[s].part1 is None:
                    raise ValueError(f"{s}.part1 필요합니다.")

        return self