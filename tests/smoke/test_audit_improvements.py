import asyncio

from hades_bot.ai.chat import HadesChat, UnsafeModelOutputError
from hades_bot.ai.fanservice import analyze_fanservice, fanservice_categories
from hades_bot.core.conversation import conversation_mode
from hades_bot.core.memory import ConversationMemory
from hades_bot.knowledge.character_data import HADES_REFERENCE


class FakeGemini:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    async def generate(self, history, user_message):
        return self.reply


def test_canonical_hades_reference_is_loaded():
    assert HADES_REFERENCE["current_team_snapshot"]["source"] == "Mimir Global Teams"
    assert HADES_REFERENCE["stable_gameplay"]["exclusive_functor"] == "Herald - Cerberus"


def test_fanservice_false_positive_guards():
    assert fanservice_categories("hear me out") == ()
    assert fanservice_categories("talk to me") == ()
    assert fanservice_categories("I need you to explain this.") == ()
    assert fanservice_categories("you've got me") == ()


def test_fanservice_analysis_has_confidence():
    analysis = analyze_fanservice("step on me")
    assert analysis.primary_category == "fan_command"
    assert analysis.confidence == "high"
    assert analysis.intensity == "bold"

    soft = analyze_fanservice("please notice me")
    assert soft.primary_category == "playful_fandom"
    assert soft.confidence == "low"


def test_emotional_turn_beats_affection_mode():
    assert conversation_mode("I had a rough day, hug me.") == "emotional"
    assert conversation_mode("step on me") == "flirtation"


def test_forbidden_generated_reply_never_enters_memory():
    async def run():
        memory = ConversationMemory(8, 3600, 10)
        chat = HadesChat(
            FakeGemini("Formula One is fascinating."),
            memory,
            max_concurrent_requests=1,
        )
        try:
            try:
                await chat.ask("guild:1:channel:2:user:3", "Tell me about Hades.")
                raise AssertionError("expected UnsafeModelOutputError")
            except UnsafeModelOutputError:
                pass
            assert await memory.message_count("guild:1:channel:2:user:3") == 0
        finally:
            await chat.close()

    asyncio.run(run())
