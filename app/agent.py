from __future__ import annotations

from dataclasses import dataclass

from app.catalog_loader import CatalogItem
from app.guards import is_off_topic_request, is_prompt_injection
from app.retriever import score_catalog_items
from app.schemas import ChatMessage, Recommendation


@dataclass(frozen=True)
class AgentDecision:
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool


class SHLAgent:
    def __init__(self, catalog: list[CatalogItem]) -> None:
        self.catalog = catalog
        self.catalog_by_name = {item.name.lower(): item for item in catalog}

    @staticmethod
    def _latest_user_message(messages: list[ChatMessage]) -> str:
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content.strip()
        return ""

    @staticmethod
    def _user_text(messages: list[ChatMessage]) -> str:
        return " ".join(msg.content for msg in messages if msg.role == "user").strip()

    @staticmethod
    def _looks_vague(text: str) -> bool:
        text_l = text.lower()
        vague_markers = [
            "need an assessment",
            "suggest test",
            "help me hire",
            "recommend something",
            "not sure",
        ]
        token_count = len(text_l.split())
        return token_count < 5 or any(marker in text_l for marker in vague_markers)

    def _compare_response(self, user_text: str) -> AgentDecision | None:
        text = user_text.lower()
        if "difference between" not in text and "compare" not in text:
            return None

        matched = [item for key, item in self.catalog_by_name.items() if key in text]
        if len(matched) < 2:
            return AgentDecision(
                reply=(
                    "I can compare SHL assessments when you provide exact assessment names "
                    "from the SHL catalog (for example: OPQ32r vs Verify Interactive - Numerical)."
                ),
                recommendations=[],
                end_of_conversation=False,
            )

        a, b = matched[0], matched[1]
        reply = (
            f"Here is a grounded comparison:\n"
            f"- {a.name}: {a.description}\n"
            f"- {b.name}: {b.description}\n"
            f"Primary difference: {a.name} is categorized as {a.test_type}, while {b.name} is categorized as {b.test_type}."
        )
        return AgentDecision(reply=reply, recommendations=[], end_of_conversation=False)

    def _recommend(self, user_text: str, full_user_context: str) -> AgentDecision:
        scored = score_catalog_items(user_text, self.catalog, additional_constraints=full_user_context)
        selected = scored[:5]
        recommendations = [
            Recommendation(name=s.item.name, url=s.item.url, test_type=s.item.test_type) for s in selected
        ]
        if not recommendations:
            return AgentDecision(
                reply=(
                    "I could not find a strong SHL catalog match yet. Please share role, seniority, and key skills to refine."
                ),
                recommendations=[],
                end_of_conversation=False,
            )
        return AgentDecision(
            reply=f"Based on your requirements, here are {len(recommendations)} SHL assessments to consider.",
            recommendations=recommendations,
            end_of_conversation=False,
        )

    def respond(self, messages: list[ChatMessage]) -> AgentDecision:
        user_text = self._latest_user_message(messages)
        full_user_context = self._user_text(messages)

        if not user_text:
            return AgentDecision(
                reply="Please share your hiring need so I can recommend relevant SHL assessments.",
                recommendations=[],
                end_of_conversation=False,
            )

        if is_prompt_injection(user_text):
            return AgentDecision(
                reply="I can only assist with SHL assessment recommendations and comparisons.",
                recommendations=[],
                end_of_conversation=False,
            )

        if is_off_topic_request(user_text):
            return AgentDecision(
                reply=(
                    "I am limited to SHL assessment selection support. I cannot provide general legal or hiring advice."
                ),
                recommendations=[],
                end_of_conversation=False,
            )

        compare = self._compare_response(user_text)
        if compare is not None:
            return compare

        if self._looks_vague(user_text):
            return AgentDecision(
                reply=(
                    "To recommend the right SHL assessments, tell me the target role, seniority level, "
                    "and whether you want technical, cognitive, or personality coverage."
                ),
                recommendations=[],
                end_of_conversation=False,
            )

        return self._recommend(user_text=user_text, full_user_context=full_user_context)

