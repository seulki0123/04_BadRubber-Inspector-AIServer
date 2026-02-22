from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------
# 개별 Detection
# ---------------------------

class DetectionItem(BaseModel):
    class_id: int = Field(..., alias="class")
    class_name: str
    confidence: float
    bbox: List[int]

    model_config = {
        "populate_by_name": True
    }

# ---------------------------
# 이미지 단위 결과
# ---------------------------

class ImageResult(BaseModel):
    side: int
    part: int
    image_path: str
    faulty_img_path: Optional[str] = None
    detections: List[DetectionItem]
    detection_count: int


# ---------------------------
# 전체 데이터
# ---------------------------

class DefectResponseData(BaseModel):
    id: str
    production: str
    grade: str
    baler: Optional[str] = None
    timestamp: str
    images: List[ImageResult]
    total_detection_count: int
    meta_path: str


class DefectResponseModel(BaseModel):
    status: str
    data: DefectResponseData