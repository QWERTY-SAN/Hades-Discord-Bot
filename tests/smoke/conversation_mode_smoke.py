from hades_bot.ai.fanservice import fanservice_category
from hades_bot.core.conversation import conversation_mode
from hades_bot.core.scope import is_hades_scope_allowed

CASES = {
    "How are you holding up?": "personal_question",
    "I'm exhausted and annoyed today.": "emotional",
    "So today I finally fixed it.": "storytelling",
    "lol that's wild": "banter",
    "What should I do tonight?": "advice",
    "How abt somewhere else very private away from prying eyes": "flirtation",
    "It's either do it or not, but I ain't backing down to someone who's like a fine looking wine": "flirtation",
    "Don't tempt me like that.": "flirtation",
    "Is that an invitation?": "flirtation",
    "Heimdall's shield is ridiculous.": "general",
}

for text, mode in CASES.items():
    assert conversation_mode(text) == mode, (text, conversation_mode(text))
    assert is_hades_scope_allowed(text), text

assert fanservice_category("Don't tempt me like that.") == "flirtation"
assert fanservice_category("Is that an invitation?") == "flirtation"

print("conversation_mode_smoke: OK")
