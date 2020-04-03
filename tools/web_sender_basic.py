#!/usr/bin/env python3
# coding: utf-8

################################################################################
# web_sender_basic
# IoTセンサ用クラウド・サービス Ambientへデータを送信します
#
# 送信方法：引数に送信値を入力してください
# ./web_sender_basic.py 123 456
#
#                                          Copyright (c) 2016-2020 Wataru KUNINO
################################################################################

#【IoTセンサ用クラウド・サービス Ambient】
# https://ambidata.io/

ambient_chid='20072'                # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='e69a37059eb44e64'     # ここにはライトキーを入力

from sys import argv
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

print(argv[0])                                  # プログラム名を表示する
if int(ambient_chid) == 0:
    print('ERROR：AmbientでチャネルIDとライトキーを取得し、記述してください')
    exit()
if len(argv) <= 1:                              # 引数が無い時
    print('Usage:',argv[0],'値1 値2 ...')       # 使用方法を表示
    exit()

url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey}           # ボディ(データ本体)用変数の定義
for i in range(1,len(argv)):                    # 引数の数だけ繰り返す
    body_dict['d'+str(i)] = argv[i]             # ボディ用変数にデータを追加
    print('d'+str(i),"=",body_dict['d'+str(i)]) # 追加したデータを表示

# クラウドへの送信処理
print(head_dict)                                # 送信ヘッダhead_dictを表示
print(body_dict)                                # 送信内容body_dictを表示
post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                # POSTリクエストデータを作成
try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(post)          # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url_s)                              # エラー内容と変数url_sを表示
res.close()                                     # HTTPアクセスの終了
print('Done')                                   # Doneを表示
