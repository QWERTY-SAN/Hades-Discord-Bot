"""Test package defaults for harmless placeholder credentials.

Smoke tests import settings but never connect to Discord or Gemini. Supplying
placeholders keeps local test runs independent of a real .env file.
"""

import os

os.environ.setdefault("DISCORD_TOKEN", "test-token-not-a-real-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-a-real-secret")
