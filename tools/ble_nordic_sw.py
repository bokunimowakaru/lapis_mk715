#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Example for Nordic SW
#
# LAPIS MK715ボードのDIPスイッチ1(P13)が変化したときに通知を受信します。
# 1. プログラムを実行するとBLEボードのスキャンを開始します。
# 2. デバイス名「cq_ex21_ble_led」を見つけると、状態変化通知を設定します。
# 3. 通知を受け取ると、DIPスイッチの値に応じてLEDをBLE通信で制御します。
#
#                                          Copyright (c) 2019-2020 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_nordic_sw.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/notifications.html

target_device  = 'cq_ex21_ble_led'                      # ここに接続するデバイス名を入力
target_service = '00001523-1212-efde-1523-785feabcd123' # ここに接続するサービスUUIDを入力

from bluepy import btle
from bluepy.btle import Peripheral, DefaultDelegate
from sys import argv
import getpass
notified_val = b'\x00'

class MyDelegate(DefaultDelegate):

    def __init__(self, params):
        DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        global notified_val
        print('\nHandle =',hex(cHandle),', Notify =',data.hex())
        if cHandle == 0x000d:
            notified_val = data

# BLE受信処理
scanner = btle.Scanner()
while True:
    try:
        devices = scanner.scan(1)
    except Exception as e:
        print("ERROR",e)
        if getpass.getuser() != 'root':
            print('使用方法: sudo', argv[0])
            exit()
    if devices is None:
        continue

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        #print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        isRohmMedal = ''
        val = ''
        for (adtype, desc, value) in dev.getScanData():
            #print("  %3d %s = %s" % (adtype, desc, value))  # ad_t=[{8:'Short Local Name'},{9:'Complete Local Name'}]
            if adtype == 9 and (value == target_device or value == 'Nordic_Blinky'):
                isRohmMedal = value
            if adtype == 7 and value == target_service:
                val = value
            if isRohmMedal == '' or val == '':
                continue
            print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
            print("    9 Complete Local Name =",isRohmMedal)
            isRohmMedal = ''
            address = dev.addr
            p = Peripheral(address, addrType='random')
            p.setDelegate(MyDelegate(DefaultDelegate))

            # Setup to turn notifications on
            p.writeCharacteristic(0x000e, b'\x01\x00')
            print('Notify config =',p.readCharacteristic(0x000e).hex())

            # Main
            print('Waiting...')
            while True:
                if p.waitForNotifications(1.0):
                    if notified_val == b'\x00':
                        led = b'\x00'
                        print('    LED = OFF')
                    else:
                        led = b'\x01'
                        print('    LED = ON')
                    p.writeCharacteristic(0x0010, led)

''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/lapis_mk715
pi@raspberrypi:~ $ cd ~/lapis_mk715
pi@raspberrypi:~/lapis_mk715 $ sudo ./ble_nordic_sw.py

Device xx:xx:xx:xx:xx:xx (random), RSSI=-47 dB, Connectable=True
    9 Complete Local Name = cq_ex21_ble_led
Notify config = 0100
Waiting...

Handle = 0xd , Notify = 01
    LED = ON

Handle = 0xd , Notify = 00
    LED = OFF

Handle = 0xd , Notify = 01
    LED = ON

Handle = 0xd , Notify = 00
    LED = OFF

--------------------------------------------------------------------------------
Gatt Toolを使った接続テストの例

pi@raspberrypi:~/lapis_mk715/tools $ gatttool -I -t random -b xx:xx:xx:xx:xx:xx
[xx:xx:xx:xx:xx:xx][LE]> connect
Attempting to connect to xx:xx:xx:xx:xx:xx
Connection successful
[xx:xx:xx:xx:xx:xx][LE]> primary
attr handle: 0x0001, end grp handle: 0x0009 uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000a, end grp handle: 0x000a uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x000b, end grp handle: 0xffff uuid: 00001523-1212-efde-1523-785feabcd123 <-- Genサービス
[xx:xx:xx:xx:xx:xx][LE]> char-desc 0x000b
handle: 0x000b, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000c, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000d, uuid: 00001524-1212-efde-1523-785feabcd123 <-- Read Notify
handle: 0x000e, uuid: 00002902-0000-1000-8000-00805f9b34fb <-- Read Notify Client Char Config
handle: 0x000f, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0010, uuid: 00001525-1212-efde-1523-785feabcd123 <-- LEDキャラクタリスティクス・ディスクリプタ
[xx:xx:xx:xx:xx:xx][LE]> char-read-hnd 000e
Characteristic value/descriptor: 00 00
[xx:xx:xx:xx:xx:xx][LE]> char-write-req 000e 01 00
Characteristic value was written successfully
Notification handle = 0x000d value: 01
Notification handle = 0x000d value: 00
Notification handle = 0x000d value: 01
Notification handle = 0x000d value: 00
'''
