from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT
import requests
import random


import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()


# domain root
@app.route("/")
def home():
    return chatgpt.prompt.generate_prompt()


@app.route("/webhook", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

def moderation(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer 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"
    }
    data = {"input": text}
    response = requests.post("https://api.openai.com/v1/moderations", headers=headers, json=data)
    response = response.json()
    return response['results'][0]['flagged']


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status

    if event.message.type != "text":
        return

    if event.message.text == "露西亞~":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="你好指揮官，等你很久了。")
        )
        return

    if event.message.text == "你先忙吧":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="好的，有需要再叫我，我隨時在你身邊！")
        )
        return
    
    if moderation(event.message.text):
        string_list = ["啊啊指揮官...等一下，好舒服","我喜歡這種感覺...繼續 *她臉漲紅的盯著你*","*她雙手擁抱你，害羞的接受你對她做的一切* 指揮官...喜歡..啊啊"]
        text = random.choice(string_list)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=text)
        )

    if working_status and not moderation(event.message.text):
        chatgpt.add_msg(event.message.text, "user")
        reply_msg = chatgpt.get_response()
        chatgpt.add_msg(reply_msg, "ai")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
