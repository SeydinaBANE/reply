from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_tokens: int = Field(default=256, gt=0, le=4096)


class CompletionResponse(BaseModel):
    completion: str
    tokens: int
    remaining: int
