import os
import threading

from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/")
def index():
    return jsonify({
        "status": "online",
        "service": "Hades Discord AI Bot",
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "hades-discord-bot",
    }), 200


def run_web_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
    )


def start_web_server() -> threading.Thread:
    thread = threading.Thread(
        target=run_web_server,
        name="render-health-server",
        daemon=True,
    )
    thread.start()
    return thread
