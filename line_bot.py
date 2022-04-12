from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
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
    if event.reply_token == "00000000000000000000000000000000":
        return
    #image_message = ImageSendMessage(
    #    type='image',
    #    originalContentUrl="https://1.bp.blogspot.com/-tVeC6En4e_E/X96mhDTzJNI/AAAAAAABdBo/jlD_jvZvMuk3qUcNjA_XORrA4w3lhPkdQCNcBGAsYHQ/s1048/onepiece01_luffy.png",
    #    previewImageUrl="https://1.bp.blogspot.com/-tVeC6En4e_E/X96mhDTzJNI/AAAAAAABdBo/jlD_jvZvMuk3qUcNjA_XORrA4w3lhPkdQCNcBGAsYHQ/s1048/onepiece01_luffy.png",
    #)

    event.message.text = event.message.text + 'あああありがとう！！！！'
    print(event.message.text)
    linebot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    #linebot_api.reply_message(event.reply_token, image_message)

@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    image_message = ImageSendMessage(
        original_content_url="https://github.com/TomoakiYasukawa/Stock_line/blob/main/Image.png",
        preview_image_url="https://github.com/TomoakiYasukawa/Stock_line/blob/main/Image.png",
    )

    event.message.text = '有無！画像だよ！'
    print(event.message.text)
    #linebot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    #linebot_api.reply_message(event.reply_token, image_message)
    #linebot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=f"https://imgsv.nikon-image.com/products/slr/lineup/d850/img/sample/pic_01_l.jpg",preview_image_url=f"https://imgsv.nikon-image.com/products/slr/lineup/d850/img/sample/pic_01_l.jpg"))
    linebot_api.reply_message(event.reply_token,image_message)

if __name__=='__main__':
    app.run()