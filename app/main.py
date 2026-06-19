from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.agent import SHLAgent
from app.catalog_loader import SHL_PREFIX, load_catalog
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="SHL Conversational Recommender")

try:
    _catalog = load_catalog()
except Exception as exc:  # pragma: no cover - startup guard
    _catalog = []
    _startup_error = str(exc)
else:
    _startup_error = ""

_agent = SHLAgent(_catalog) if _catalog else None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    if _agent is None:
        raise HTTPException(status_code=503, detail=f"Catalog unavailable: {_startup_error}")

    decision = _agent.respond(payload.messages)

    # Hard safety check: recommendations must map to SHL URLs.
    for rec in decision.recommendations:
        if not str(rec.url).startswith(SHL_PREFIX):
            raise HTTPException(status_code=500, detail="Recommendation URL outside SHL catalog")

    return ChatResponse(
        reply=decision.reply,
        recommendations=decision.recommendations,
        end_of_conversation=decision.end_of_conversation,
    )

