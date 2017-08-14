from flask import *
import telegram
import html
import json
import os

app = Flask(__name__)
bot = telegram.Bot(token=os.environ.get("TOKEN"))

@app.route("/gogs/<chat_id>", methods=["POST"])
def process(chat_id):
    data = json.loads(request.data.decode())
    for commit in reversed(data["commits"]):
        bot.sendMessage(
            chat_id=chat_id, 
            text="<b>{0}</b> hat gerade <a href='{1}'>{2}</a> commited:\n<pre>{3}</pre>".format(commit["author"]["name"], commit["url"], commit["id"], html.escape(commit["message"])),
            parse_mode="html",
            disable_web_page_preview=True)
    return ""
