from hades_bot.scope import is_hades_scope_allowed, scope_block_reason

allowed = [
    "Hades, tell me about the Society of Muses.",
    "What do you think of puppetry?",
    "How are you feeling, Hades?",
    "Tell me about Divine Grace.",
    "What happened with Mintha and Leuce?",
]
blocked = [
    "Hades, what do you think about Formula One?",
    "Tell me the latest NBA scores.",
    "Write me a Python script.",
    "What is the weather tomorrow?",
    "How does a CPU work?",
    "Who won the election?",
]

for text in allowed:
    assert is_hades_scope_allowed(text), text
for text in blocked:
    assert not is_hades_scope_allowed(text), text

assert scope_block_reason("Hades, what do you think about Formula One?") == "F1 or motorsport"
print("scope smoke checks passed")
