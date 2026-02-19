import os
import time
import requests
import sentry_sdk
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler



load_dotenv()

# ---------- Envs ----------------
SENTRY_DSN=os.getenv("SENTRY_DSN")
SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN=os.getenv("SLACK_APP_TOKEN")
HCA_USERCHECK_URL=os.getenv("HCA_USERCHECK_URL")
# --------------------------------

# -------- Sentry Init ----------
sentry_sdk.init(
    dsn=SENTRY_DSN
)
# --------------------------------


# ---------- Slack Init ----------
app=App(token=SLACK_BOT_TOKEN)
print("Running!")
# --------------------------------

@app.event("app_mention")
def ping_pongs(say, event):
    if "ping" not in event.get("text"):
        return
    msg_ts= event["ts"] # Record msg timestamp
    lat = time.time() - float(msg_ts)
    say(f"Pong! Latency: {lat}")

@app.command("/gatekeeper_about")
def what_is_this_help_me(ack, respond, command):
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


@app.event("member_joined_channel")
def check_newbie_member_idv(event, say):
    user_id = event["user"]
    response = requests.get(HCA_USERCHECK_URL, params={"slack_id" : user_id})
    data=response.json()
    result = data["result"]

    if result == ("verified_eligible", "verified_but_over_18"):
        say(f"<@{user_id}> passed the IDV check.")
    elif result in ("needs_submission", "not_found", "rejected", "pending"):
        say(f"<@{user_id}> failed the IDV check.")


@app.command("/gatekeeper_kick_non_idv")
def kick_out_members(ack, respond, command):
    ack()

    channel_id = command["channel_id"]
    invoker_user_id = command["user_id"]
    target_id = command["text"].strip().strip("<@>").split("|")[0]

    channel_info = app.client.conversations_info(channel=channel_id)
    channelmanager = channel_info["channel"].get("creator")

    if invoker_user_id != channelmanager:
        respond("You are not the channel manager to run this command on this channel.")
        return
    

    members = []
    cursor = None
    while True:
        result = app.client.conversations_members(channel=channel_id, cursor=cursor)
        members.extend(result["members"])
        cursor = result.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    kicked = []
    for user_id in members:
        user_info = app.client.users_info(user=user_id)
        if user_info["user"].get("is_bot"):
            continue

        response = requests.get(HCA_USERCHECK_URL, params={"slack_id" : user_id})
        data = response.json()
        idv_result = data["result"]

        if idv_result not in ("verified_eligible", "verified_but_over_18"):
            try:
                app.client.conversations_kick(channel=channel_id, user=user_id)
                kicked.append(user_id)
            except Exception as e:
                print(f"Failed to kick {user_id}. {e}")

        
    kicked_list = "\n".join(f"• <@{uid}>" for uid in kicked) or "None"
    respond(text=f"Kicked {len(kicked)} non-IDV verified member(s):\n{kicked_list}")





@app.command("/gatekeeper_scan")
def scan_all_members_idv(ack, respond, command):
    ack()

    channel_id = command["channel_id"]
    invoker_user_id = command["user_id"]

    channel_info = app.client.conversations_info(channel=channel_id)
    channelmanager = channel_info["channel"].get("creator")

    if invoker_user_id != channelmanager:
        respond("You are not the channel manager to run this command on this channel.")
        return

    
    members = []
    cursor = None
    while True:
        result = app.client.conversations_members(channel=channel_id, cursor=cursor)
        members.extend(result["members"])
        cursor = result.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    passed = []
    passed18 = []
    failed = []

    for user_id in members:

        user_info = app.client.users_info(user=user_id)
        if user_info["user"].get("is_bot"):
            continue
             # Since Slackbot is disabled in HC Slack (sadge), we wont need to check if Slackbot is in our channel.
        response = requests.get(HCA_USERCHECK_URL, params={"slack_id" : user_id})
        data = response.json()
        result = data ["result"]


        if result in ("verified_eligible"):
            passed.append(user_id)
        elif result in ("verified_but_over_18"):
            passed18.append(user_id)
        else:
            failed.append(user_id)

    passed_list = "\n".join(f"• <@{uid}>" for uid in passed) or "None"
    passed18_list = "\n".join(f"• <@{uid}>" for uid in passed18) or "_None_"
    failed_list = "\n".join(f"• <@{uid}>" for uid in failed) or "None"

    respond(
        text=f"Scan finished.\n\n"
        f"*IDV Verified ({len(passed)}):*\n{passed_list}\n\n"
        f"*IDV Verified but over 18 ({len(passed18)}):*\n{passed18_list}\n\n"
        f"*Not IDV verified ({len(failed)}):*\n{failed_list}\n\n"
    )





















if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()