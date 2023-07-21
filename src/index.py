import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from src.llm import LLM

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
llm = LLM()


# domain root
@app.route("/")
def home():
    return llm.prompt.generate_prompt()


@app.route("/webhook", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)    
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status

    if event.message.type != "text":
        return

    if event.message.text == "你在嗎":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=">_<")
        )
        return

    if event.message.text == "你先忙吧":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="zzZ")
        )
        return
    
    if working_status:
        llm.add_msg(event.message.text, "user")
        reply_msg = llm.get_response()
        llm.add_msg(reply_msg, "ai")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
