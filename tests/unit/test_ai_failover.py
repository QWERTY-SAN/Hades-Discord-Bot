import asyncio
from types import SimpleNamespace

import pytest

from hades_bot.ai.providers.router import AIProviderRouter, ProviderChainError


def make_router(gemini_generate, groq_generate):
    router = object.__new__(AIProviderRouter)
    router.gemini_provider = SimpleNamespace(generate=gemini_generate)
    router.groq_provider = SimpleNamespace(generate=groq_generate)
    router.last_successful_model = None
    router.fallback_count = 0
    router.groq_fallback_count = 0
    return router


def test_groq_runs_after_both_gemini_models_fail_and_uses_tool_free_prompt():
    attempted_models = []
    groq_calls = []

    async def fail_model(*, model, **kwargs):
        attempted_models.append(model)
        raise RuntimeError(f"{model} unavailable")

    async def groq_generate(**kwargs):
        groq_calls.append(kwargs)
        return "Groq handled the request."

    router = make_router(fail_model, groq_generate)
    contents = [SimpleNamespace(role="user", parts=[SimpleNamespace(text="Hello, Hades.")])]
    fallback_contents = [SimpleNamespace(role="user", parts=[SimpleNamespace(text="Tool-free prompt")])]

    response = asyncio.run(
        router.generate(
            contents=contents,
            config=SimpleNamespace(system_instruction="Respond as Hades."),
            fallback_contents=fallback_contents,
            fallback_config=SimpleNamespace(system_instruction="Respond as Hades."),
        )
    )

    assert attempted_models == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
    assert groq_calls[0]["contents"] is fallback_contents
    assert groq_calls[0]["model"] == "llama-3.3-70b-versatile"
    assert response.text == "Groq handled the request."
    assert router.groq_fallback_count == 1
    assert router.last_successful_model == "groq:llama-3.3-70b-versatile"


def test_gemini_31_success_does_not_call_groq():
    attempted_models = []
    groq_calls = []

    async def gemini_generate(*, model, **kwargs):
        attempted_models.append(model)
        if model == "gemini-3.5-flash-lite":
            raise RuntimeError("primary unavailable")
        return SimpleNamespace(text="Gemini 3.1 recovered.")

    async def groq_generate(**kwargs):
        groq_calls.append(kwargs)
        return "This should not be used."

    router = make_router(gemini_generate, groq_generate)
    response = asyncio.run(
        router.generate(
            contents=[],
            config=SimpleNamespace(system_instruction="Respond as Hades."),
        )
    )

    assert attempted_models == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
    assert groq_calls == []
    assert response.text == "Gemini 3.1 recovered."
    assert router.fallback_count == 1
    assert router.groq_fallback_count == 0
    assert router.last_successful_model == "gemini-3.1-flash-lite"


def test_gemini_auth_failure_skips_second_model_and_uses_groq():
    attempted_models = []
    groq_calls = []

    async def fail_auth(*, model, **kwargs):
        attempted_models.append(model)
        error = RuntimeError("Gemini key rejected")
        error.status_code = 401
        raise error

    async def groq_generate(**kwargs):
        groq_calls.append(kwargs)
        return "Groq fallback."

    router = make_router(fail_auth, groq_generate)
    response = asyncio.run(
        router.generate(
            contents=[],
            config=SimpleNamespace(system_instruction="Respond as Hades."),
        )
    )

    assert attempted_models == ["gemini-3.5-flash-lite"]
    assert len(groq_calls) == 1
    assert response.text == "Groq fallback."
    assert router.groq_fallback_count == 1


def test_all_providers_failing_raises_a_chain_error():
    async def fail_gemini(*, model, **kwargs):
        raise RuntimeError("Gemini unavailable")

    async def fail_groq(**kwargs):
        raise RuntimeError("Groq unavailable")

    router = make_router(fail_gemini, fail_groq)

    with pytest.raises(ProviderChainError, match="All configured AI providers"):
        asyncio.run(
            router.generate(
                contents=[],
                config=SimpleNamespace(system_instruction="Respond as Hades."),
            )
        )

def test_empty_primary_response_moves_to_the_next_gemini_model():
    attempted_models = []

    async def gemini_generate(*, model, **kwargs):
        attempted_models.append(model)
        if model == "gemini-3.5-flash-lite":
            return SimpleNamespace(text="")
        return SimpleNamespace(text="Gemini 3.1 returned a usable reply.")

    async def groq_generate(**kwargs):
        raise AssertionError("Groq should not be called when Gemini 3.1 returns text.")

    router = make_router(gemini_generate, groq_generate)
    response = asyncio.run(
        router.generate(
            contents=[],
            config=SimpleNamespace(system_instruction="Respond as Hades."),
        )
    )

    assert attempted_models == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
    assert response.text == "Gemini 3.1 returned a usable reply."
    assert router.last_successful_model == "gemini-3.1-flash-lite"

