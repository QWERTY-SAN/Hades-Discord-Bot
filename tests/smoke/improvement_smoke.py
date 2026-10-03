from hades_bot.core.scope import is_hades_scope_allowed, forbidden_topic_category
from hades_bot.knowledge.lore import build_aether_context
assert not is_hades_scope_allowed("Hades, what do you think about Formula One?")
assert not is_hades_scope_allowed("Hades, talk to me about basketball.")
assert is_hades_scope_allowed("Heimdall likes horse racing, right?")
assert is_hades_scope_allowed("Tell me about Hades's Music Dossier.")
assert forbidden_topic_category("Hades, what do you think about F1?") == "F1 or motorsport"
ctx = build_aether_context("What about her Functor?", conversation_text="Tell me about Hades and her Divine Grace.")
assert "Hades identity reference" in ctx
assert "Exclusive Functor" in ctx
print("improvement smoke tests passed")
