from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pya3rt
#from flask_ngrok import run_with_ngrok

app = Flask(__name__)
#run_with_ngrok(app)

linebot_api = LineBotApi('Jt8umdac9vN41JG++pWR3+hw3AApqKB7df5Xs4wu+UhuKV5ZbyuNbHxhs+gthYDmT1uGP4CCW8TVFOTvJYaw5h9QABuV5\
SAKFFP4g4n0eVTWw8WchByQJ8bfigRgQCiqtp8dfPYj0VIoFkgPIJap+AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('885c8b905b482fc4bd24e7199bda56ca')

@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    linebot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

if __name__=='__main__':
    app.run()