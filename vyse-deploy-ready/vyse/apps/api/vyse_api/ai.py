"""Provider-agnostic AI layer. Real OpenAI implementation + an offline stub so the
whole pipeline runs without an API key. Swap providers by changing get_ai()."""
from __future__ import annotations

import hashlib
import json
from typing import Protocol

from .settings import get_settings

settings = get_settings()

# ---- structured-output JSON schemas (map 1:1 to DB columns) -------------------
PULSE_SCHEMA = {
    "type": "object",
    "properties": {
        "hook_type": {"type": "string"},
        "cta_type": {"type": "string"},
        "emotion": {"type": "array", "items": {"type": "string"}},
        "story_pattern": {"type": "string"},
        "content_pillar": {"type": "string"},
    },
    "required": ["hook_type", "cta_type", "emotion", "story_pattern", "content_pillar"],
}

WHY_SCHEMA = {
    "type": "object",
    "properties": {
        "why_it_worked": {"type": "string"},
        "trigger_type": {"type": "array", "items": {"type": "string"}},
        "success_factors": {"type": "object"},
        "replication_insights": {"type": "string"},
    },
    "required": ["why_it_worked", "trigger_type", "replication_insights"],
}

FORGE_SCHEMA = {
    "type": "object",
    "properties": {
        "hooks": {"type": "array", "items": {"type": "string"}},
        "script": {"type": "string"},
        "shotlist": {"type": "array", "items": {"type": "string"}},
        "ctas": {"type": "array", "items": {"type": "string"}},
        "framework": {"type": "string"},
    },
    "required": ["hooks", "script", "shotlist", "ctas", "framework"],
}


class AIProvider(Protocol):
    async def structured(self, *, system: str, user: str, schema: dict, model: str) -> dict: ...
    async def embed(self, *, texts: list[str], model: str) -> list[list[float]]: ...
    async def transcribe(self, *, audio_url: str) -> str: ...


class StubProvider:
    """Deterministic, offline. Lets the pipeline run end-to-end with no key."""

    async def structured(self, *, system, user, schema, model) -> dict:
        keys = schema.get("properties", {})
        if "hook_type" in keys:
            return {
                "hook_type": "curiosity_gap",
                "cta_type": "follow_for_more",
                "emotion": ["curiosity", "aspiration"],
                "story_pattern": "problem_solution",
                "content_pillar": "education",
            }
        if "why_it_worked" in keys:
            return {
                "why_it_worked": "(stub) Strong open-loop hook + high information density "
                "rewarded saves. Replace with a real OpenAI key for live reasoning.",
                "trigger_type": ["curiosity", "social_proof"],
                "success_factors": {"hook": "open_loop", "pacing": "fast"},
                "replication_insights": "Lead with the payoff promise; keep first 2s tight.",
            }
        return {
            "hooks": ["Hook A (stub)", "Hook B (stub)", "Hook C (stub)"],
            "script": "(stub) 30s script blueprint. Add OPENAI_API_KEY for real output.",
            "shotlist": ["0-2s talking head", "2-10s b-roll", "10-25s payoff"],
            "ctas": ["Save this", "Follow for part 2"],
            "framework": "problem_solution",
        }

    async def embed(self, *, texts, model) -> list[list[float]]:
        # deterministic pseudo-embedding from a hash; fine for offline dev/search demos
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            vec = [(b - 128) / 128 for b in (h * (settings.embed_dim // 32 + 1))]
            out.append(vec[: settings.embed_dim])
        return out

    async def transcribe(self, *, audio_url) -> str:
        return ""


class OpenAIProvider:
    def __init__(self, key: str):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=key)

    async def structured(self, *, system, user, schema, model) -> dict:
        resp = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "out", "schema": schema, "strict": False},
            },
        )
        return json.loads(resp.choices[0].message.content)

    async def embed(self, *, texts, model) -> list[list[float]]:
        resp = await self.client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]

    async def transcribe(self, *, audio_url) -> str:
        import httpx

        async with httpx.AsyncClient() as c:
            audio = (await c.get(audio_url)).content
        resp = await self.client.audio.transcriptions.create(
            model="whisper-1", file=("audio.mp3", audio)
        )
        return resp.text


def get_ai() -> AIProvider:
    if settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key)
    return StubProvider()
