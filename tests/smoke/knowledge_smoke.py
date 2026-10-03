from hades_bot.knowledge.lore import build_aether_context

checks = {
    "Shifted Stars": ["Shifted Star", "daily", "weekly", "monthly"],
    "Swigs": ["Swigs"],
    "Zero Time": ["Zero Time"],
    "Heimdall": ["Heimdall"],
    "Gengchen": ["Gengchen"],
}

for query, needles in checks.items():
    context = build_aether_context(query)
    for needle in needles:
        assert needle.lower() in context.lower(), (query, needle, context)

print("knowledge_smoke: OK")
