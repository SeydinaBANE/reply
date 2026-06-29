from pydantic import BaseModel, Field


class Passage(BaseModel):
    document_id: str
    content: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    top_k: int | None = Field(default=None, ge=1, le=50)


class QueryResponse(BaseModel):
    answer: str
    sources: list[Passage]


class IngestRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=256, pattern=r"^[\w.\-:/]+$")
    content: str = Field(min_length=1, max_length=200_000)


class IngestResponse(BaseModel):
    document_id: str
    chunks: int
