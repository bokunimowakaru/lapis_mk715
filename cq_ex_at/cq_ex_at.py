#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE AT Sender cq_ex_at_test
#
# ATコマンド + VSSPPで数値(テキスト)を送信します。
#
# Python用シリアル通信ライブラリ pySerialが必要です
# pip3 install pyserial
#
# 引数はシリアルポート名です。
# ./cq_ex_at_test.py /dev/ttyS2  # Windows COM3の場合
#
#                                          Copyright (c) 2020 Wataru KUNINO
################################################################################

# 参考文献
# https://pyserial.readthedocs.io/en/latest/pyserial_api.html

PORT = '/dev/ttyUSB2'                           # シリアルポートの初期値
TIMEOUT = 30.0                                  # 接続までの待機時間(秒)
INTERVAL = 5.0                                  # データ送信間隔(0より大・秒)

from sys import argv                            # 引数の入力用ライブラリを追加
import serial                                   # Python用シリアル通信ライブラリ
from time import sleep                          # timeからsleepを組み込む

print('BLE AT Sender (usage: ' + argv[0] + ' [port名(省略可)]')

def lapis_tx(ser, tx):                          # シリアル送信を行う関数を定義
    print('>', tx.strip())                      # 送信内容を表示
    ser.write((tx).encode())                    # シリアル送信を実行

def lapis_rx(ser, timeout = 0.3):               # シリアル受信を行う関数を定義
    tries = int(timeout / 0.3)                  # 受信実行回数(整数)をtriesへ
    while(tries > 0):                           # 変数triesの値が1以上
        res = ser.read_until().decode().strip() # 改行(\r\n)まで受信を実行
        if res == '':                           # 何も受信しなかったとき
            tries -= 1                          # 変数triesを1減算
        else:                                   # 受信した時
            print('<', res)                     # 受信内容を表示
            return res                          # 受信内容を応答
    return ''                                   # 空文字を応答

def lapis_at(ser, at, timeout = 0.9):           # ATコマンドを送受信する関数定義
    lapis_tx(ser, at + '\r')                    # ATコマンドを送信
    return lapis_rx(ser, timeout)               # ATコマンドの応答を応答

argc = len(argv)                                # 引数の数をargcへ代入
port = PORT                                     # シリアルポート名を変数portへ
if argc >= 2:                                   # 入力パラメータ数の確認
    if argv[1][0:3].lower() == 'com' and argv[1][3:].isnumeric():
        i = int(argv[1][3:]) - 1
        port = '/dev/ttyS' + str(i)
    elif argv[1][0:5] != '/dev/':
        port = '/dev/' + argv[1]
    else:
        port = argv[1]                          # ポート番号を設定
print('Serial Port :',port)                     # シリアルポート名を表示
try:                                            # シリアルポートの初期化
    ser = serial.Serial(port, 57600, rtscts = True, timeout = 0.3)
except Exception as e:                          # 例外処理発生時
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

res = lapis_at(ser, 'AT')                       # [A][T][Enter]送信
if res != 'OK' and res != 'NO CARRIER':         # 応答値を確認
    print('ATコマンドの応答がありませんでした')
    exit()                                      # プログラムの終了

res = lapis_at(ser, 'ATD', TIMEOUT)             # [A][T][D][Enter]送信
if res != 'CONNECT':                            # 応答値を確認
    print('Bluetooth接続がありませんでした')
    exit()                                      # プログラムの終了

i=0
while(1):
    lapis_tx(ser, str(i))
    res = lapis_rx(ser, INTERVAL)
    i += 1
    if res == 'NO CARRIER':
        break
print('Bluetooth接続が切断されました')
ser.close()
