#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE AT Sender cq_ex_at_2_temp_basic Raspberry Pi 専用
#
# ATコマンド + VSSPP で Raspberry Pi の CPU 温度を送信します。
#
# Python用シリアル通信ライブラリ pySerialが必要です
# pip3 install pyserial
#
#                                          Copyright (c) 2020 Wataru KUNINO
################################################################################

# 参考文献
# https://pyserial.readthedocs.io/en/latest/pyserial_api.html

PORT = '/dev/ttyUSB0'                           # シリアルポートの初期値

import serial                                   # Python用シリアル通信ライブラリ
from time import sleep                          # timeからsleepを組み込む
from tempSensor import TempSensor               # tempSensor.pyの組み込み

print('BLE AT Sender')                          # タイトルを表示

tempSensor = TempSensor()                       # 温度センサの実体化
ser = serial.Serial(PORT, 57600, rtscts=True, timeout=0.3) # シリアルの初期化
ser.write(('AT\r').encode())                    # [A][T][Enter]送信
ser.write(('ATD\r').encode())                   # [A][T][D][Enter]送信
print('> ATD')

i = 0                                           # 送信データ用変数i
while True:                                     # ループ
    res = ser.read_until().decode().strip()     # 改行(\r\n)まで受信
    if len(res) > 0:                            # 受信文字列がある時
        print('<', res)                         # 受信内容を表示
    if res == 'NO CARRIER':                     # 切断を検出
        break                                   # ループを抜ける
    if res == 'CONNECT':                        # 接続を検出
        sleep(10)                               # 10秒間の待ち時間処理
        i = 1                                   # 送信を開始
    if i > 0:                                   # i>0のとき
        temp = tempSensor.get()                 # 温度測定の実行
        print('Temperature =', temp)            # 測定結果を表示する
        ser.write(str(temp).encode())           # シリアル送信を実行
        sleep(5)                                # 5秒間の待ち時間処理
        i += 1                                  # 変数iに1を加算

del tempSensor                                  # 温度センサを終了
ser.close()                                     # シリアルポートを閉じる

''' 実行例

pi@raspberrypi:~/lapis_mk715/tools $ ./cq_ex_at_2_temp_basic.py
BLE AT Sender
> ATD
< OK
< CONNECT
Temperature = 30.8
Temperature = 30.3
Temperature = 29.8

'''
