#!/usr/bin/env python3
# coding: utf-8

################################################################################
# web_sender_ambient (旧 ambient_router)
# IoTセンサ用クラウド・サービス Ambientへデータを送信します
#
# 送信方法：引数に送信値を入力してください
# ./web_sender_ambient.py 123 456
#
#                                          Copyright (c) 2016-2020 Wataru KUNINO
################################################################################

#【IoTセンサ用クラウド・サービス Ambient】
# https://ambidata.io/

ambient_chid='00000'                # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力

from sys import argv
from time import sleep
from random import random
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime

print(argv[0])                                  # プログラム名を表示する
if int(ambient_chid) == 0:
    print('重要：AmbientでチャネルIDとライトキーを取得し、記述してください')
    print('30秒後に下記へ送信します。[ctrl]+[C]で送信キャンセル')
    print('https://ambidata.io/ch/channel.html?id=725')
    ambient_chid='725'
    ambient_wkey='ad3e53b54fe16764'
    sleep(30)

url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey}           # ボディ(データ本体)用変数の定義

print('ambient_chid =',ambient_chid)            # チャネルIDを表示
print('ambient_wkey =',ambient_wkey)            # ライトキーを表示
argc = len(argv)                                # 引数の数をargcへ代入
date = datetime.datetime.today()
print(date.strftime('%Y/%m/%d %H:%M'))
for i in range(1,9,1):
    if argc <= i:                               # 入力パラメータ数の確認
        #argv.append(str(random()))             # 乱数を追加
        body_dict['d'+str(i)] = str(random())
    else:
        body_dict['d'+str(i)] = argv[i]
    #print('d'+str(i),"=",argv[i])
    print('d'+str(i),"=",body_dict['d'+str(i)])

# クラウドへの送信処理
print(head_dict)                                # 送信ヘッダhead_dictを表示
print(body_dict)                                # 送信内容body_dictを表示
post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                # POSTリクエストデータを作成
try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(post)          # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url_s)                              # エラー内容と変数url_sを表示
res_str = res.read().decode()                   # 受信テキストを変数res_strへ
res.close()                                     # HTTPアクセスの終了
if len(res_str):                                # 受信テキストがあれば
    print('Response:', res_str)                 # 変数res_strの内容を表示
else:
    print('Done')                               # Doneを表示
