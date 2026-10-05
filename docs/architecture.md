# Architecture

```text
Hades-Discord-Bot/
├── hades_bot/
│   ├── bot.py
│   ├── config.py
│   ├── core/
│   │   ├── conversation.py
│   │   ├── memory.py
│   │   ├── scope.py
│   │   └── utils.py
│   ├── ai/
│   │   ├── chat.py
│   │   ├── gemini_client.py
│   │   └── persona.py
│   ├── knowledge/
│   │   ├── character_data.py
│   │   └── lore.py
│   └── media/
│       ├── gifs.py
│       └── media.py
├── data/
│   └── aether_gazer/
│       ├── game_knowledge.json
│       ├── terminology.json
│       ├── source_policy.json
│       ├── sources.json
│       └── characters/
│           ├── hades.json
│           └── hades_reference.json
├── docs/
├── tests/
│   └── smoke/
├── main.py
├── render.yaml
└── .env.example
```

The runtime is grouped by responsibility: core bot infrastructure, AI generation/persona, knowledge retrieval, media, and external reference data.
