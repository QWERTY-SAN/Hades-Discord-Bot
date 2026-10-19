# Documentation index

Start with the [root README](../README.md) for installation, commands, configuration, and the current AI fallback chain.

| Guide | Contents |
|---|---|
| [Architecture](architecture.md) | Package layout, request lifecycle, AI providers, and testing conventions |
| [Deployment](deployment.md) | Render setup, required secrets, local Windows run, and troubleshooting |
| [Knowledge](knowledge.md) | Structured Aether Gazer data and retrieval behavior |
| [Fan-service](fanservice.md) | Contextual flirtation and Hades-specific reaction guidance |
| [Conversation improvements](CONVERSATION_IMPROVEMENTS.md) | Conversation behavior and regression notes |
| [Changelog](../CHANGELOG.md) | Release-by-release history |

## Where changes belong

- Read-only dashboard UI and browser behavior: `hades_bot/static/`
- Dashboard/status/health HTTP routes: `hades_bot/web.py`
- Discord commands and message routing: `hades_bot/bot.py`
- AI orchestration and provider fallback: `hades_bot/ai/`
- Memory, scope decisions, and conversational signals: `hades_bot/core/`
- Local lore and live-source selection: `hades_bot/knowledge/`
- GIF/image selection and delivery: `hades_bot/media/`
- Versioned lore and gameplay facts: `data/aether_gazer/`
- Standalone runtime/contract checks: `tests/smoke/`
- Pytest unit and regression tests: `tests/unit/`
