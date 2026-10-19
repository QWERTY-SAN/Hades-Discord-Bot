import asyncio
import time

from hades_bot.core.memory import ConversationMemory


def test_memory_history_and_reset():
    async def run():
        memory = ConversationMemory(8, 3600, 10)
        key = "guild:1:channel:2:user:3"
        assert not await memory.has_history(key)
        async with memory.session(key) as session:
            session.commit("Hello", "Greetings.")
        assert await memory.has_history(key)
        assert await memory.message_count(key) == 2
        snapshot = await memory.snapshot(key)
        assert snapshot == [
            {"role": "user", "content": "Hello"},
            {"role": "model", "content": "Greetings."},
        ]
        await memory.reset(key)
        assert not await memory.has_history(key)

    asyncio.run(run())

def test_memory_uses_an_even_history_limit():
    memory = ConversationMemory(5, 3600, 10)
    assert memory.max_history == 6


def test_expired_history_is_not_resurrected_by_a_new_session():
    async def run():
        memory = ConversationMemory(8, 60, 10)
        key = "guild:1:channel:2:user:expired"
        async with memory.session(key) as session:
            session.commit("Old question", "Old answer.")

        # Simulate an idle conversation that outlived its TTL.
        memory._conversations[key].touched_at = time.monotonic() - 61
        async with memory.session(key) as session:
            assert session.history == []
            session.commit("New question", "New answer.")

        assert await memory.snapshot(key) == [
            {"role": "user", "content": "New question"},
            {"role": "model", "content": "New answer."},
        ]

    asyncio.run(run())
