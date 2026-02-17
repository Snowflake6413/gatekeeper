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

@app.command("/gatekeeper_about")
def what_is_this_help_me(ack, respond, commannd):
    ack()

    about_blocks = [
        		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Gatekeeper is a Slack bot that channel managers can use to help manage unwanted people from their channel."
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "You can manage your channel members and check if they meet your factors. If they dont, you can kick them out with one single command."
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a WIP, more info to be added."
			}
		}
    ]
  
    respond(blocks=about_blocks)






















if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()