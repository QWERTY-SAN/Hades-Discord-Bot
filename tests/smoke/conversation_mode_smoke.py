from hades_bot.ai.fanservice import fanservice_category
from hades_bot.core.conversation import conversation_mode, conversation_thread_guidance
from hades_bot.core.scope import is_hades_scope_allowed

CASES = {
    "How are you holding up?": "personal_question",
    "I'm exhausted and annoyed today.": "emotional",
    "So today I finally fixed it.": "storytelling",
    "lol that's wild": "banter",
    "Woahhh :Pepeuwu:": "banter",
    "Ayooo": "banter",
    "💀": "banter",
    "What should I do tonight?": "advice",
    "What else can we do together?": "social_planning",
    "Let's hang out sometime.": "social_planning",
    "how abt to drink some tea???": "casual",
    "Want some tea?": "casual",
    "Ok, what do u like then?": "casual",
    "How abt somewhere else very private away from prying eyes": "flirtation",
    "It's either do it or not, but I ain't backing down to someone who's like a fine looking wine": "flirtation",
    "Don't tempt me like that.": "flirtation",
    "Is that an invitation?": "flirtation",
    "Heimdall's shield is ridiculous.": "general",
    "I'm hungry": "food_chat",
    "What food do you like?": "food_chat",
    "What's your favorite dessert?": "food_chat",
    "This chicken stew looks delicious.": "food_chat",
    "I'm craving ramen.": "food_chat",
    "What should we eat?": "food_chat",
    "I love adobo": "food_chat",
    "a date?": "flirtation",
    "Will you be my date?": "flirtation",
    "Let's go on a date together": "flirtation",
    "I'm so down bad for you": "flirtation",
    "You're making it hard to behave": "flirtation",
    "If you keep looking at me like that...": "flirtation",
    "Only for u": "personal_gesture",
    "Are you fine?": "check_in",
    "Good morning amigo, I found ancient golem in the old world, shall I give you as a gift?": "gift_offer",
    "No, I meant the other one.": "correction",
        }

for text, mode in CASES.items():
    assert conversation_mode(text) == mode, (text, conversation_mode(text))
    assert is_hades_scope_allowed(text), text

assert fanservice_category("Don't tempt me like that.") == "flirtation"
assert fanservice_category("Is that an invitation?") == "flirtation"
assert conversation_mode("what's this?") == "continuation"
assert conversation_mode("No, I meant the other one.") == "correction"
assert conversation_mode("and") == "general"

fanservice_history = [
    {"role": "user", "content": "Hades, you're gorgeous."},
    {"role": "model", "content": "How shameless of you."},
]
thread = conversation_thread_guidance(fanservice_history, "What should I do tonight?")
assert "FAN-SERVICE CARRYOVER RULE" in thread
pivot_thread = conversation_thread_guidance(fanservice_history, "Anyway, what about Shifted Stars?")
assert "TOPIC PIVOT" in pivot_thread

print("conversation_mode_smoke: OK")
