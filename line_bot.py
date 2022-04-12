from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
import pya3rt
from flask_ngrok import run_with_ngrok
import pandas as pd
import investpy
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import datetime
import talib as ta
import gc
import os

app = Flask(__name__)
run_with_ngrok(app)

linebot_api = LineBotApi('Jt8umdac9vN41JG++pWR3+hw3AApqKB7df5Xs4wu+UhuKV5ZbyuNbHxhs+gthYDmT1uGP4CCW8TVFOTvJYaw5h9QABuV5\
SAKFFP4g4n0eVTWw8WchByQJ8bfigRgQCiqtp8dfPYj0VIoFkgPIJap+AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('885c8b905b482fc4bd24e7199bda56ca')

def get_dfs_stock(stock_number, from_data, to_data, interval):
    number = '{}'.format(stock_number)
    dfs = investpy.get_stock_historical_data(
        stock=number,
        country='japan',
        from_date=from_data,
        to_date=to_data,
        interval=interval
    )

    return dfs

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

    #event.message.text = event.message.text + 'あああありがとう！！！！'
    #print(event.message.text)
    #linebot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    dt_now = datetime.datetime.now()

    dfs = get_dfs_stock(event.message.text, '01/01/2019', dt_now.strftime('%d/%m/%Y'), 'Weekly')
    # dfs = get_dfs_stock(Index, '01/01/2019', dt_now.strftime('%d/%m/%Y'), 'Weekly')
    dfs_long = get_dfs_stock(event.message.text, '01/01/2015', dt_now.strftime('%d/%m/%Y'), 'Monthly')
    # tec = get_tec('7201')

    date, closep, highp, lowp, openp, volume = dfs.index, dfs['Close'], dfs['High'], dfs['Low'], dfs['Open'], dfs[
        'Volume']
    date_long, closep_long = dfs_long.index, dfs_long['Close']

    # SMA
    sma13 = ta.SMA(closep, timeperiod=13)
    sma26 = ta.SMA(closep, timeperiod=26)
    sma52 = ta.SMA(closep, timeperiod=52)
    # RSI
    RSI = ta.RSI(closep, timeperiod=14)
    # STOCK
    fastk, fastd = ta.STOCHF(highp, lowp, closep, fastk_period=14, fastd_period=14, fastd_matype=3)
    slowtk, slowtd = ta.STOCH(highp, lowp, closep, fastk_period=14, slowk_period=3)
    # MACD
    macd, macdsignal, macdhist = ta.MACD(closep, fastperiod=12, slowperiod=26, signalperiod=9)
    # DMI
    ADX = ta.ADX(highp, lowp, closep, timeperiod=14)
    P_DI = ta.PLUS_DI(highp, lowp, closep, timeperiod=14)
    M_DI = ta.MINUS_DI(highp, lowp, closep, timeperiod=14)

    fig = plt.figure()
    fig.set_figheight(12)
    fig.set_figwidth(16)
    dt_now = datetime.datetime.now()
    fig.suptitle("{} : {}".format(event.message.text, dt_now.strftime('%Y/%m/%d')), fontname="MS Gothic", fontsize=40)

    ax1 = fig.add_subplot(3, 2, 1)
    # ax1.set_xlim([pd.to_datetime('2019-01-28'), pd.to_datetime('2021-01-29')])
    ax1.set_xlim([dfs.index[14], dfs.index[-1]])
    ax7 = ax1.twinx()
    ax7.bar(closep.index, volume, color="red", width=2.0, label="Volume")
    ax1.plot(closep.index, closep, "black", label="Stock")
    ax1.plot(closep.index, sma13, "purple", label="SMA13")
    ax1.plot(closep.index, sma26, "green", label="SMA26")
    ax1.plot(closep.index, sma52, "blue", label="SMA52")
    ax1.set_ylabel('Stock Value')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax1.set_zorder(2)
    ax7.set_zorder(1)
    ax1.patch.set_alpha(0)

    ax6 = fig.add_subplot(3, 2, 2)
    ax6.plot(date_long, closep_long, "black", label="Stock")
    ax6.set_ylabel('Stock Value')
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax2 = fig.add_subplot(3, 2, 3)
    ax2.plot(RSI.index, RSI, "purple", label="RSI")
    ax2.set_ylabel('RSI')
    ax2.set_xlim([dfs.index[14], dfs.index[-1]])
    ax2.hlines([30], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax2.hlines([70], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax2.hlines([50], dfs.index[1], dfs.index[-1], "black", linestyles='dashed')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax3 = fig.add_subplot(3, 2, 5)
    ax3.plot(fastk.index, fastk, "b", label="Fast%K")
    ax3.plot(slowtd.index, slowtd, "r", label="Slow%D")
    ax3.set_ylabel('STOCH')
    ax3.set_xlim([dfs.index[14], dfs.index[-1]])
    ax3.hlines([20], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax3.hlines([80], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax4 = fig.add_subplot(3, 2, 4)
    ax4.plot(macd.index, macd, "b", label="MACD")
    ax4.plot(macdsignal.index, macdsignal, "r", label="Signal")
    ax4.bar(macdhist.index, macdhist, color="red", width=5.0, label="Histogram")
    ax4.set_ylabel('MACD')
    ax4.set_xlim([dfs.index[14], dfs.index[-1]])
    ax4.hlines([0], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax5 = fig.add_subplot(3, 2, 6)
    ax5.plot(ADX.index, ADX, "r", label="ADX2")
    ax5.plot(P_DI.index, P_DI, "b", label="+DI")
    ax5.plot(M_DI.index, M_DI, "orange", label="-DI")
    ax5.set_ylabel('ADX,DMI')
    ax5.set_xlim([dfs.index[14], dfs.index[-1]])
    ax5.hlines([20], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    # fig.tight_layout()

    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()
    ax5.grid()
    ax6.grid()

    ax1.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax2.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax3.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax4.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax5.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax6.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    # plt.show()
    filename = "{}.png" .format(event.message.text)
    fig.savefig(filename)


    plt.cla()
    plt.clf()
    plt.close('all')
    plt.close(fig)
    del date, closep, highp, lowp, openp, volume, sma13, sma26, sma52, RSI, fastk, fastd, slowtk, slowtd, macd, macdsignal, macdhist, ADX, P_DI, M_DI
    gc.collect()

    os.system('git init')
    os.system('git add .')
    os.system('git commit -am "make it better"')
    os.system('git remote add origin https://github.com/TomoakiYasukawa/Stock_image.git')
    os.system('git push origin master')

    time.sleep(5)

    image_message = ImageSendMessage(
        original_content_url="https://keen-halva-ba4ecd.netlify.app/{}.png".format(event.message.text),
        preview_image_url="https://keen-halva-ba4ecd.netlify.app/{}.png".format(event.message.text),
    )

    print(ImageSendMessage)

    linebot_api.reply_message(event.reply_token,image_message)


@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    image_message = ImageSendMessage(
        original_content_url="https://bejewelled-jelly-e19b4e.netlify.app/stockimage.png",
        preview_image_url="https://bejewelled-jelly-e19b4e.netlify.app/stockimage.png",
    )

    #event.message.text = '有無！画像だよ！'
    #print(event.message.text)
    linebot_api.reply_message(event.reply_token,image_message)

    dt_now = datetime.datetime.now()

    dfs = get_dfs_stock('7201', '01/01/2019', '25/08/2021', 'Weekly')
    # dfs = get_dfs_stock(Index, '01/01/2019', dt_now.strftime('%d/%m/%Y'), 'Weekly')
    dfs_long = get_dfs_stock('7201', '01/01/2015', dt_now.strftime('%d/%m/%Y'), 'Monthly')
    # tec = get_tec('7201')

    date, closep, highp, lowp, openp, volume = dfs.index, dfs['Close'], dfs['High'], dfs['Low'], dfs['Open'], dfs[
        'Volume']
    date_long, closep_long = dfs_long.index, dfs_long['Close']

    # SMA
    sma13 = ta.SMA(closep, timeperiod=13)
    sma26 = ta.SMA(closep, timeperiod=26)
    sma52 = ta.SMA(closep, timeperiod=52)
    # RSI
    RSI = ta.RSI(closep, timeperiod=14)
    # STOCK
    fastk, fastd = ta.STOCHF(highp, lowp, closep, fastk_period=14, fastd_period=14, fastd_matype=3)
    slowtk, slowtd = ta.STOCH(highp, lowp, closep, fastk_period=14, slowk_period=3)
    # MACD
    macd, macdsignal, macdhist = ta.MACD(closep, fastperiod=12, slowperiod=26, signalperiod=9)
    # DMI
    ADX = ta.ADX(highp, lowp, closep, timeperiod=14)
    P_DI = ta.PLUS_DI(highp, lowp, closep, timeperiod=14)
    M_DI = ta.MINUS_DI(highp, lowp, closep, timeperiod=14)

    #fig = plt.figure()
    fig.set_figheight(12)
    fig.set_figwidth(16)
    dt_now = datetime.datetime.now()
    fig.suptitle("test-testet : {}".format(dt_now.strftime('%Y/%m/%d')), fontname="MS Gothic", fontsize=40)

    ax1 = fig.add_subplot(3, 2, 1)
    # ax1.set_xlim([pd.to_datetime('2019-01-28'), pd.to_datetime('2021-01-29')])
    ax1.set_xlim([dfs.index[14], dfs.index[-1]])
    ax7 = ax1.twinx()
    ax7.bar(closep.index, volume, color="red", width=2.0, label="Volume")
    ax1.plot(closep.index, closep, "black", label="Stock")
    ax1.plot(closep.index, sma13, "purple", label="SMA13")
    ax1.plot(closep.index, sma26, "green", label="SMA26")
    ax1.plot(closep.index, sma52, "blue", label="SMA52")
    ax1.set_ylabel('Stock Value')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax1.set_zorder(2)
    ax7.set_zorder(1)
    ax1.patch.set_alpha(0)

    ax6 = fig.add_subplot(3, 2, 2)
    ax6.plot(date_long, closep_long, "black", label="Stock")
    ax6.set_ylabel('Stock Value')
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax2 = fig.add_subplot(3, 2, 3)
    ax2.plot(RSI.index, RSI, "purple", label="RSI")
    ax2.set_ylabel('RSI')
    ax2.set_xlim([dfs.index[14], dfs.index[-1]])
    ax2.hlines([30], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax2.hlines([70], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax2.hlines([50], dfs.index[1], dfs.index[-1], "black", linestyles='dashed')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax3 = fig.add_subplot(3, 2, 5)
    ax3.plot(fastk.index, fastk, "b", label="Fast%K")
    ax3.plot(slowtd.index, slowtd, "r", label="Slow%D")
    ax3.set_ylabel('STOCH')
    ax3.set_xlim([dfs.index[14], dfs.index[-1]])
    ax3.hlines([20], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax3.hlines([80], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax4 = fig.add_subplot(3, 2, 4)
    ax4.plot(macd.index, macd, "b", label="MACD")
    ax4.plot(macdsignal.index, macdsignal, "r", label="Signal")
    ax4.bar(macdhist.index, macdhist, color="red", width=5.0, label="Histogram")
    ax4.set_ylabel('MACD')
    ax4.set_xlim([dfs.index[14], dfs.index[-1]])
    ax4.hlines([0], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    ax5 = fig.add_subplot(3, 2, 6)
    ax5.plot(ADX.index, ADX, "r", label="ADX2")
    ax5.plot(P_DI.index, P_DI, "b", label="+DI")
    ax5.plot(M_DI.index, M_DI, "orange", label="-DI")
    ax5.set_ylabel('ADX,DMI')
    ax5.set_xlim([dfs.index[14], dfs.index[-1]])
    ax5.hlines([20], dfs.index[1], dfs.index[-1], "red", linestyles='dashed')
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))

    # fig.tight_layout()

    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()
    ax5.grid()
    ax6.grid()

    ax1.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax2.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax3.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax4.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax5.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    ax6.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0, fontsize=10)
    # plt.show()
    filename = "test.png"  # .format(Sector, Label, Index)
    fig.savefig(filename)

    # 送りたい内容
    # send_contents = '{}の株価情報でーす↓↓↓↓'.format(Label)
    # TOKEN_dic = {'Authorization': 'Bearer' + ' ' + TOKEN}
    # send_dic = {'message': send_contents}
    # 画像ファイルのパスを指定
    # image_file = './Technical_index/{}.png'.format(Label)

    # LINEに画像とメッセージを送る
    # binary = open(image_file, mode='rb')
    # 指定の辞書型にする
    # image_dic = {'imageFile': binary}
    # requests.post(api_url, headers=TOKEN_dic, data=send_dic, files=image_dic)
    # time.sleep(3)
    plt.cla()
    plt.clf()
    plt.close('all')
    plt.close(fig)
    del date, closep, highp, lowp, openp, volume, sma13, sma26, sma52, RSI, fastk, fastd, slowtk, slowtd, macd, macdsignal, macdhist, ADX, P_DI, M_DI
    gc.collect()

if __name__=='__main__':
    app.run()