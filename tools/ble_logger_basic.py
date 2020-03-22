#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger
#
# LAPIS MK715用 cq_ex11_ble_sw, cq_ex12_ble_temp, cq_ex13_ble_hum
#
# cq_ex11_ble_sw, cq_ex12_ble_temp, cq_ex13_ble_hum が送信するビーコンを受信し
# ビーコンに含まれる、温度センサ値（humは湿度センサ値）を表示します。
#
#                                          Copyright (c) 2019-2020 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_sens_scan.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html
#   https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf

interval = 1.01                                 # 動作間隔

from bluepy import btle                         # bluepyからbtleを組み込む
from time import sleep                          # timeからsleepを組み込む

def payval(num, bytes=1, sign=False):           # 受信データから値を抽出する
    global val                                  # 受信データ用変数valを読み込む
    a = 0                                       # 戻り値用変数aを定義する
    if num < 2 or len(val) < (num - 2 + bytes) * 2:
        print('ERROR: data length',len(val))
        return 0
    for i in range(0, bytes):                   # バイト数分の値を変数aに代入
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:                                    # 符号つきの場合
        if a >= 2 ** (bytes * 8 - 1):           # マイナス値のとき
            a -= 2 ** (bytes * 8)               # マイナス値へ変換
    return a                                    # 得られた値aを応答する

def printval(dict, name, n, unit):              # 受信値を表示する関数
    value = dict.get(name)                      # 変数dict内の項目nameの値を取得
    if value == None:                           # 項目が無かったとき
        return                                  # 戻る
    if type(value) is not str:                  # 値が文字列で無かったとき
        value = round(value,n)                  # 小数点以下第n位で丸める
    print('    ' + name + ' ' * (14 - len(name)) + '=', value, unit)    # 表示

scanner = btle.Scanner()                        # インスタンスscannerを生成
while True:                                     # 永久ループ
    devices = scanner.scan(interval)            # BLEデバイスをスキャンする
    for dev in devices:                         # 見つかった各デバイスについて
        isRohmMedal = ''                        # 対象デバイス・フラグのクリア
        val = ''                                # 取得値のクリア
        for (adtype, desc, value) in dev.getScanData():
            # ビーコンがNordic nRF5かどうかを確認する
            if (adtype == 8 or adtype == 9) and (value  == 'nRF5x'):
                isRohmMedal = 'Nordic nRF5'
            if desc == 'Manufacturer':
                val = value
            if isRohmMedal != 'Nordic nRF5' or val == '':
                continue
            # Nordic nRF5 受信時の処理
            print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
            print('    isRohmMedal   =',isRohmMedal)
            sensors = dict()                    # 辞書型変数sensorsの初期化
            sensors['ID'] = hex(payval(2,2))    # ビーコン内のID(0x0059)を取得
            sensors['Button'] = format(payval(6), '04b')    # ボタン状態を取得
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536    # 温度
            sensors['Humidity'] = payval(7,2) / 65536 * 100 # 湿度を取得
            sensors['SEQ'] = payval(9)          # 送信番号を取得
            sensors['RSSI'] = dev.rssi          # RSSI(受信強度)を取得
            printval(sensors, 'ID', 0, '')
            printval(sensors, 'SEQ', 0, '')
            printval(sensors, 'Button', 0, '')
            printval(sensors, 'Temperature', 2, '℃')
            printval(sensors, 'Humidity', 2, '%')
            printval(sensors, 'RSSI', 0, 'dB')

''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/lapis_mk715
pi@raspberrypi:~ $ cd ~/lapis_mk715/tools
pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_logger_basic.py

Device xx:xx:xx:xx:xx:xx (random), RSSI=-51 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 0
    Button        = 1111
    Temperature   = 19.05 ℃
    Humidity      = 76.96 %
    RSSI          = -51 dB

Device xx:xx:xx:xx:xx:xx (random), RSSI=-47 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 1
    Button        = 1111
    Temperature   = 19.07 ℃
    Humidity      = 76.96 %
    RSSI          = -47 dB

Device xx:xx:xx:xx:xx:xx (random), RSSI=-51 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 2
    Button        = 1111
    Temperature   = 19.07 ℃
    Humidity      = 76.96 %
    RSSI          = -51 dB
'''
