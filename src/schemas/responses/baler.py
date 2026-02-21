from pydantic import BaseModel


class BalerResponseData(BaseModel):
    id: str
    production: str
    grade: str
    timestamp: str
    baler: int
    # confidence: float


class BalerResponseModel(BaseModel):
    status: str
    data: BalerResponseData