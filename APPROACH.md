# Approach Document (Draft)

## Problem Framing

The service must produce grounded SHL assessment recommendations through stateless multi-turn conversations. The assignment imposes strict constraints: fixed response schema, recommendation scope restricted to SHL catalog URLs, max 8-turn conversation budget, and 30-second response timeout.

## Architecture

The implementation is organized into five layers:

1. **Catalog layer (`catalog_loader.py`)**  
   Loads and validates assessment entries from `data/processed/catalog.json`, enforces SHL-only URLs, deduplicates by URL, and normalizes fields.

2. **Guardrail layer (`guards.py`)**  
   Detects off-topic requests and prompt-injection patterns before recommendation logic runs.

3. **Retrieval layer (`retriever.py`)**  
   Token-overlap ranking over name, description, tags, and levels to produce deterministic, explainable candidate ordering.

4. **Agent policy layer (`agent.py`)**  
   Supports required conversational behaviors:
   - clarify vague requests before recommendation
   - recommend once sufficient detail appears
   - refine naturally via full history context
   - compare known assessments using catalog-grounded details
   - refuse out-of-scope or unsafe prompts

5. **API layer (`main.py`)**  
   Exposes `GET /health` and `POST /chat`, validates request/response via Pydantic, and performs final URL safety assertions.

## Prompting / Decision Strategy

This version prioritizes deterministic policy for evaluator reliability over generative freedom:

- Clarification is triggered for short/vague user asks.
- Recommendation triggers only when intent is specific enough.
- Comparison activates only if at least two catalog items are identified from user text.
- Refusal responses always return empty recommendations.

This policy minimizes hallucination and schema drift.

## Evaluation Strategy

Local checks include:

- API unit tests for health, clarify behavior, recommendation output shape, and refusal behavior.
- `scripts/eval_local.py` to replay trace files and enforce schema + SHL URL constraints.

Future improvements for stronger Recall@10:

- richer scraped metadata
- embedding-based retrieval hybridized with lexical search
- constraint weighting (role/seniority/skills/personality priorities)

## Iteration Notes

What did not work well in early prototypes:

- purely free-form LLM responses (high schema and hallucination risk)
- recommendation-on-first-turn behavior for vague queries (fails behavior probes)

What improved outcomes:

- strict response model validation
- explicit guardrails and operation routing
- catalog URL hard checks before returning results

## AI Tooling Disclosure

AI-assisted development was used to speed implementation and test scaffolding. Final architecture, guardrails, and evaluator compliance logic were designed to be interview-defensible and deterministic.

