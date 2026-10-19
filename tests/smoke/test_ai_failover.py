import asyncio
from types import SimpleNamespace

from hades_bot.ai.gemini_client import GeminiService


def test_groq_runs_after_both_gemini_models_fail():
    service = object.__new__(GeminiService)
    attempted_models = []

    async def fail_model(model, contents, config, fallback_contents, fallback_config):
        attempted_models.append(model)
        raise RuntimeError(f"{model} unavailable")

    async def groq_create(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Groq handled the request.")
                )
            ]
        )

    service.model_hierarchy = lambda: (
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    )
    service._request_model = fail_model
    service.groq_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=groq_create)
        )
    )
    service.groq_fallback_count = 0
    service.fallback_count = 0
    service.last_successful_model = None

    response = asyncio.run(
        service._generate_with_model_hierarchy(
            contents=[
                SimpleNamespace(
                    role="user",
                    parts=[SimpleNamespace(text="Hello, Hades.")],
                )
            ],
            config=SimpleNamespace(system_instruction="Respond as Hades."),
        )
    )

    assert attempted_models == [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ]
    assert response.text == "Groq handled the request."
    assert service.groq_fallback_count == 1
    assert service.last_successful_model.startswith("groq:")
