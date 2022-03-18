import hashlib
import hmac
import html
import json
import os
from urllib import request

import telegram
from flask import *

app = Flask(__name__)
bot = telegram.Bot(token=os.environ.get("TOKEN"))
webhook_secret = os.environ.get("WEBHOOK_SECRET")


def is_signature_valid(request_signature, data):
    data_signature = hmac.new(webhook_secret.encode('utf-8'), data, hashlib.sha1).hexdigest()
    return hmac.compare_digest(data_signature, request_signature)


@app.route("/gogs/<chat_id>", methods=["POST"])
def process(chat_id):
    if webhook_secret:
        if "X-Hub-Signature" not in request.headers or not is_signature_valid(
                request.headers.get("X-Hub-Signature").split('=')[1], request.data):
            return "", 403

    data = json.loads(request.data.decode())
    if "commits" not in data:
        return ""

    text = "[<a href=\"{repo_url}\">{repo}</a>:<a href=\"{compare_url}\">{branch}</a>]: {count} new commit{s}\n".format(
            repo_url=data["repository"]["url"],
            repo=data["repository"]["full_name"],
            compare_url=data["compare"],
            branch=data["ref"].split("/")[-1],
            count=len(data["commits"]),
            s="s" if len(data["commits"]) > 1 else ""
    )
    for commit in reversed(data["commits"]):
        text += "[<a href=\"{url}\">{sha}</a>] <code>{msg}</code> - {author}\n".format(
                url=commit["url"],
                sha=commit["id"][:7],
                msg=html.escape(commit["message"]),
                author=html.escape(commit["author"]["name"])
        )

    bot.sendMessage(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
    return ""

@app.route("/mail/<chat_id>", methods=["POST"])
def process_mailgun(chat_id):
    data = json.loads(request.data.decode())
    bot.sendMessage(chat_id=chat_id, text=data["stripped-text"], disable_web_page_preview=True)