import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
knowledge = json.loads((ROOT / 'data' / 'aether_gazer' / 'game_knowledge.json').read_text())
hades = json.loads((ROOT / 'data' / 'aether_gazer' / 'characters' / 'hades_reference.json').read_text())

assert 'events_and_event_endgame' in knowledge
assert 'service_lifecycle' in knowledge
assert 'endgame_and_late_game' in knowledge
assert 'shifted_star_routine' in knowledge
assert hades['current_team_snapshot']['source_last_update'] == '2026-09-28'
assert 'Puppet Master - Hades' in hades['current_team_snapshot']['team']

media = (ROOT / 'hades_bot' / 'media' / 'media.py').read_text()
assert 'content=entry.url' not in media
assert 'set_image(url=url)' in media

print('current build smoke checks passed')
