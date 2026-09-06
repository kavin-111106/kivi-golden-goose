from pydantic import BaseModel, Field
from enum import Enum

class ObservationCreate(BaseModel):
    observed: str
    intended: str


class ObservationResponse(BaseModel):
    observed: str
    intended: str
    message: str

class TransformRequest(BaseModel):
    text: str

class TransformResponse(BaseModel):
    original: str
    transformed: str

class MemoryStatus(str, Enum):
    candidate = "candidate"
    confirmed = "confirmed"
    disabled = "disabled"

class MemoryUpdate(BaseModel):
    canonical: str | None = None
    variants: str | None = None
    status: MemoryStatus | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )