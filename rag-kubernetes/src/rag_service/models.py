from pydantic import BaseModel, Field


class Passage(BaseModel):
    document_id: str
    content: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[Passage]
