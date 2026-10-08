"""Build and runtime version information for the Hades bot."""

APP_NAME = "Hades Discord Bot"
APP_VERSION = "1.4.0"


def short_commit() -> str:
    import os

    commit = os.getenv("RENDER_GIT_COMMIT", "local")
    return commit[:8] if commit else "unknown"


def branch() -> str:
    import os

    return os.getenv("RENDER_GIT_BRANCH", "local") or "unknown"


def runtime() -> str:
    import os

    return "Render" if os.getenv("RENDER") else "local"
