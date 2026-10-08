# Hades Discord Bot 2.1.0

## Conversation quality
- Social-planning turns now have their own intent mode.
- Simple acknowledgements now receive brief, natural handling guidance.
- Relationship-status fan-service has its own semantic cue class.
- Hades-adjacent art and craft topics are more naturally admitted by scope.

## Persona quality
- Added an explicit natural-closure rule to suppress overly formal responses to "okay", "fair enough", and similar turns.
- Added social-planning guidance so Hades can answer what she would actually do with the Administrator.
- Ordinary companionship remains distinct from automatic romance.

## Runtime
- Health and runtime metrics now use a lock because Discord and aiohttp run in separate threads.
- Off-topic refusal wording has small category-specific variation.
- Added regression coverage for the new behavior.

## Gemini
- Kept dynamic response generation.
- Did not add a fixed fan-service response bank.
- Left Gemini 3.x sampling defaults untouched.
