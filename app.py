from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import openai
import traceback

app = Flask(__name__)

# 環境變數
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 確保環境變數有值
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET or not OPENAI_API_KEY:
    raise ValueError("環境變數未設置，請確認 Vercel 的 `Environment Variables` 是否正確！")

# 設定 Line Bot API
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 設定 OpenAI API
openai.api_key = OPENAI_API_KEY
openai.api_base = "https://free.v36.cm/v1"


# GPT 回應函數
def GPT_response(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-mini",
            messages=[{"role": "user", "content": text}],
            temperature=0.5,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(traceback.format_exc())
        return " AI 服務異常，請稍後再試！"


# Webhook 監聽
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理使用者訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        reply_text = GPT_response(msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_text))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage("發生錯誤，請稍後再試！"))


# Vercel Serverless 處理函數
def handler(event, context):
    return app(event, context)

