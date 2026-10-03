# Knowledge maintenance

Stable lore and game terminology live alongside version-sensitive gameplay/event data.

When adding a new system:
1. Add the knowledge to `data/aether_gazer/game_knowledge.json`.
2. Add stable terminology/aliases to `terminology.json` when needed for retrieval.
3. Add source metadata to `sources.json`.
4. Keep exact rates, reset schedules, banner rotations, rewards, and meta recommendations labeled as dated/version-sensitive.
5. Add a smoke test if the term is important to scope or retrieval.

Gacha/scan information is knowledge only; this bot does not implement a virtual gacha command system.


## Gacha spending terminology

The knowledge layer understands F2P/free-to-play, low spender, dolphin, whale, and spender as informal player-spending labels. These are discussion terminology, not official Aether Gazer account classifications. No gacha command or spending tracker is implemented.
