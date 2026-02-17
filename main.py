import os
import time
import sentry_sdk
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler



load_dotenv()

# ---------- Envs ----------------
SENTRY_DSN=os.getenv("SENTRY_DSN")
SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN=os.getenv("SLACK_APP_TOKEN")
# --------------------------------

# -------- Sentry Init ----------
sentry_sdk.init(
    dsn=SENTRY_DSN
)
# --------------------------------


# ---------- Slack Init ----------
app=App(token=SLACK_BOT_TOKEN)
# --------------------------------

@app.event("app_mention")
def ping_pongs(say, event):
    if "ping" not in event.get("text"):
        return
    msg_ts= event["ts"] # Record msg timestamp
    lat = time.time() - float(msg_ts)
    say(f"Pong! Latency: {lat}")

@app.command("/about")























if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()