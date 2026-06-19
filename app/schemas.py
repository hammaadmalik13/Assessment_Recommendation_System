from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage] = Field(min_length=1, max_length=30)


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    url: HttpUrl
    test_type: str = Field(min_length=1, max_length=10)


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str = Field(min_length=1)
    recommendations: list[Recommendation]
    end_of_conversation: bool

    @model_validator(mode="after")
    def validate_recommendation_count(self) -> "ChatResponse":
        rec_count = len(self.recommendations)
        if rec_count not in (0,) and not (1 <= rec_count <= 10):
            raise ValueError("recommendations must be empty or have 1..10 items")
        return self

