from pydantic import BaseModel, ConfigDict, Field


class LogRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model: str = Field(min_length=1)
    features: list[float]
    prediction: float
    latency_ms: float = Field(ge=0)


class DriftRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model: str = Field(min_length=1)
    reference: list[list[float]]
    current: list[list[float]]


class DriftResponse(BaseModel):
    psi: float
    level: str
