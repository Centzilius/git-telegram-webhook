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
            text="<b>{0}</b> hat gerade <a href='{1}'>{2}</a> in <b>{3}</b> commited:\n<pre>{4}</pre>".format(
                commit["author"]["name"],
                commit["url"],
                commit["id"],
                data["repository"]["name"],
                html.escape(commit["message"])
            ),
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
    return ""
